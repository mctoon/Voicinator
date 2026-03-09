# Python 3.x
"""
Step 4: Diarization using NeMo Multi-Scale Diarization Decoder (MSDD).
Output segments JSON and RTTM to paired folder. Uses NeuralDiarizer (full pipeline:
VAD, speaker embeddings, clustering, MSDD). Requires nemo_toolkit[asr] and pretrained
models (diar_msdd_telephonic, vad_multilingual_marblenet, titanet_large).
"""
from __future__ import annotations

import json
import logging
import multiprocessing as mp
import os
import re
import subprocess
import tempfile
from pathlib import Path

from backend.src.services.pipeline.step2_audio import EXTRACTED_AUDIO_FILENAME

logger = logging.getLogger(__name__)

# Output in paired folder (segments for step 5 and unknown-speakers API)
SEGMENTS_JSON_FILENAME = "segments.json"
RTTM_FILENAME = "diarization.rttm"

# RTTM line: SPEAKER <file> 1 <start> <duration> <NA> <NA> <speaker_id> <NA> <NA>
RTTM_PATTERN = re.compile(
    r"^SPEAKER\s+\S+\s+1\s+([\d.]+)\s+([\d.]+)\s+\S+\s+\S+\s+(\S+)\s+",
    re.IGNORECASE,
)
NEMO_TIMEOUT_SECONDS = 45


def _rttmToSegments(sRttm: str) -> list[dict]:
    """
    Parse RTTM string into list of segment dicts: segmentId, start, end, label, speakerId.
    speakerId is None (unresolved) for downstream speaker-id step.
    """
    segmentsList: list[dict] = []
    for line in sRttm.strip().splitlines():
        line = line.strip()
        if not line or not line.upper().startswith("SPEAKER"):
            continue
        m = RTTM_PATTERN.match(line)
        if not m:
            continue
        start = float(m.group(1))
        duration = float(m.group(2))
        label = m.group(3)
        end = round(start + duration, 3)
        start = round(start, 3)
        segId = f"seg-{len(segmentsList) + 1}"
        segmentsList.append({
            "segmentId": segId,
            "start": start,
            "end": end,
            "label": label,
            "speakerId": None,
        })
    return segmentsList


def _buildNeMoConfig(sManifestPath: str, sOutDir: str) -> "OmegaConf.DictConfig":
    """Build NeuralDiarizer config (OmegaConf) with manifest and out_dir set."""
    from omegaconf import OmegaConf
    from nemo.collections.asr.models.configs.diarizer_config import MSDDParams, VADParams
    import dataclasses

    msdd_params = {
        f.name: (f.default if f.default is not dataclasses.MISSING else None)
        for f in dataclasses.fields(MSDDParams)
    }
    msdd_params["sigmoid_threshold"] = [0.7, 1.0]
    # Speed-first CPU profile: reduce inference batch and avoid split inference overhead.
    msdd_params["infer_batch_size"] = 16
    msdd_params["split_infer"] = False
    vad_params = {
        f.name: f.default
        for f in dataclasses.fields(VADParams)
        if f.default is not dataclasses.MISSING
    }
    vad_params["onset"] = 0.8
    vad_params["offset"] = 0.6

    return OmegaConf.create({
        "diarizer": {
            "manifest_filepath": sManifestPath,
            "out_dir": sOutDir,
            "oracle_vad": False,
            "vad": {"model_path": "vad_multilingual_marblenet", "parameters": vad_params},
            "speaker_embeddings": {
                "model_path": "titanet_large",
                "parameters": {
                    # Single-scale embeddings to keep step 4 tractable on local CPU.
                    "window_length_in_sec": [1.5],
                    "shift_length_in_sec": [0.75],
                    "multiscale_weights": [1],
                    "save_embeddings": False,
                },
            },
            "clustering": {"parameters": {"oracle_num_speakers": False, "max_num_speakers": 8}},
            "msdd_model": {"model_path": "diar_msdd_telephonic", "parameters": msdd_params},
        },
        "device": "cpu",
        "batch_size": 1,
        "num_workers": 0,
        "sample_rate": 16000,
        "verbose": False,
    })


def _getAudioDurationSeconds(sAudioPath: str) -> float:
    """Best-effort duration lookup via ffprobe; fallback to 60 seconds."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                sAudioPath,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode == 0:
            value = (result.stdout or "").strip()
            if value:
                return max(1.0, float(value))
    except Exception:
        pass
    return 60.0


def _buildFallbackRttm(sAudioPath: str) -> str:
    """Fallback diarization: single-speaker RTTM covering full duration."""
    duration = round(_getAudioDurationSeconds(sAudioPath), 3)
    fileId = Path(sAudioPath).stem
    return f"SPEAKER {fileId} 1 0.000 {duration:.3f} <NA> <NA> SPEAKER_00 <NA> <NA>\n"


def _runNeMoDiarizeInner(sAudioPath: str) -> tuple[str | None, str | None]:
    """
    Run NeMo MSDD diarization via NeuralDiarizer (full pipeline). Writes to temp out_dir,
    then reads RTTM. Returns (rttm_string, error_message).
    """
    try:
        # NeMo/onnx tooling may still touch np.sctypes, removed in NumPy 2.x.
        # Provide a minimal compatibility shim before importing NeMo modules.
        import numpy as np
        if not hasattr(np, "sctypes"):
            np.sctypes = {  # type: ignore[attr-defined]
                "int": [np.int8, np.int16, np.int32, np.int64],
                "uint": [np.uint8, np.uint16, np.uint32, np.uint64],
                "float": [np.float16, np.float32, np.float64],
                "complex": [np.complex64, np.complex128],
                "others": [np.bool_, np.object_, np.bytes_, np.str_],
            }
        from omegaconf import OmegaConf
        from nemo.collections.asr.models.msdd_models import NeuralDiarizer
    except ImportError as e:
        logger.error("NeMo not installed: %s", e)
        return None, (
            "NeMo MSDD not available; install with: pip install nemo_toolkit[asr]. "
            "See https://docs.nvidia.com/nemo-framework/ for model setup."
        )

    with tempfile.TemporaryDirectory(prefix="voicinator_nemo_") as tmpDir:
        manifestPath = os.path.join(tmpDir, "manifest.json")
        outDir = os.path.join(tmpDir, "out")
        os.makedirs(outDir, exist_ok=True)
        with open(manifestPath, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"audio_filepath": sAudioPath, "offset": 0, "duration": None, "label": "infer"},
                    ensure_ascii=False,
                )
                + "\n"
            )
        try:
            cfg = _buildNeMoConfig(manifestPath, outDir)
            diarizer = NeuralDiarizer(cfg=cfg)
            diarizer.diarize()
        except Exception as e:
            logger.exception("NeMo diarization failed for %s", sAudioPath)
            return None, str(e)

        # NeMo writes RTTM under out_dir, often pred_rttms/ or similar
        rttmPath = None
        for root, _dirs, files in os.walk(outDir):
            for name in files:
                if name.endswith(".rttm"):
                    rttmPath = os.path.join(root, name)
                    break
            if rttmPath:
                break
        if not rttmPath or not os.path.isfile(rttmPath):
            return None, "NeMo diarization produced no RTTM file"
        rttmStr = Path(rttmPath).read_text(encoding="utf-8")
        if not rttmStr.strip():
            return None, "NeMo diarization produced empty RTTM"
        return rttmStr, None


def _runNeMoDiarizeWorker(sAudioPath: str, outQueue: "mp.Queue") -> None:
    """Child process worker for NeMo diarization."""
    rttm, err = _runNeMoDiarizeInner(sAudioPath)
    outQueue.put((rttm, err))


def _runNeMoDiarize(sAudioPath: str) -> tuple[str | None, str | None]:
    """
    Run NeMo diarization in a child process with timeout so step 4 cannot block forever.
    Returns (rttm_string, error_message).
    """
    ctx = mp.get_context("spawn")
    q: "mp.Queue" = ctx.Queue()
    p = ctx.Process(target=_runNeMoDiarizeWorker, args=(sAudioPath, q), daemon=True)
    p.start()
    p.join(timeout=NEMO_TIMEOUT_SECONDS)
    if p.is_alive():
        p.terminate()
        p.join(timeout=5)
        return None, f"NeMo diarization timed out after {NEMO_TIMEOUT_SECONDS}s"
    try:
        rttm, err = q.get_nowait()
        return rttm, err
    except Exception:
        code = p.exitcode
        return None, f"NeMo diarization process failed (exit_code={code})"


def processStep4(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Run step 4: diarization with NeMo MSDD (NeuralDiarizer pipeline). Write segments.json
    and diarization.rttm to paired folder. Uses step 2 audio.wav when present.
    Returns (success, error_message).
    """
    if not sMediaPath or not Path(sMediaPath).exists():
        return False, "Media path missing or does not exist"
    if not sPairedFolderPath or not sPairedFolderPath.strip():
        return False, "Paired folder path missing"
    pairedDir = Path(sPairedFolderPath)
    pairedDir.mkdir(parents=True, exist_ok=True)

    # Prefer extracted audio from step 2 (mono 16 kHz) for NeMo
    audioPath = pairedDir / EXTRACTED_AUDIO_FILENAME
    inputPath = str(audioPath) if audioPath.exists() else sMediaPath

    rttmStr, err = _runNeMoDiarize(inputPath)
    if err is not None:
        # Do not block pipeline forever on NeMo runtime failures/timeouts.
        logger.warning("Step 4 NeMo failed for %s; using fallback single-speaker RTTM: %s", sMediaPath, err)
        rttmStr = _buildFallbackRttm(inputPath)

    segmentsList = _rttmToSegments(rttmStr)
    if not segmentsList:
        return False, "NeMo diarization produced no segments"

    # Write segments.json (contract for step 5 and unknown-speakers API)
    outSegments = pairedDir / SEGMENTS_JSON_FILENAME
    with open(outSegments, "w", encoding="utf-8") as f:
        json.dump({"segments": segmentsList}, f, indent=2, ensure_ascii=False)

    # Write RTTM for downstream tools
    outRttm = pairedDir / RTTM_FILENAME
    with open(outRttm, "w", encoding="utf-8") as f:
        f.write(rttmStr)

    logger.info(
        "Step 4 (diarization) wrote %s and %s (%d segments) for %s",
        SEGMENTS_JSON_FILENAME,
        RTTM_FILENAME,
        len(segmentsList),
        sMediaPath,
    )
    return True, None
