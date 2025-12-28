"""Miners API Router - Top-level router for mining algorithms."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/miners", tags=["Miners"])


class MinerInfo(BaseModel):
    """Mining algorithm information."""
    id: str
    name: str
    description: str
    output_format: str
    supports_ocpm: bool = False
    parameters: List[dict] = []


AVAILABLE_MINERS = [
    MinerInfo(
        id="inductive",
        name="Inductive Miner",
        description="Discovers process models using process tree structures. Produces sound models with good fitness/precision balance.",
        output_format="petri_net",
        supports_ocpm=False,
        parameters=[
            {"name": "noise_threshold", "type": "float", "default": 0.0, "description": "Filter infrequent behavior"}
        ]
    ),
    MinerInfo(
        id="inductive_imf",
        name="Inductive Miner - Infrequent",
        description="Variant that handles infrequent behavior better by filtering.",
        output_format="petri_net",
        supports_ocpm=False,
        parameters=[
            {"name": "noise_threshold", "type": "float", "default": 0.2, "description": "Noise filtering threshold"}
        ]
    ),
    MinerInfo(
        id="alpha",
        name="Alpha Miner",
        description="Classic process mining algorithm. Best for simple structured logs without loops.",
        output_format="petri_net",
        supports_ocpm=False,
        parameters=[]
    ),
    MinerInfo(
        id="alpha_plus",
        name="Alpha+ Miner",
        description="Extension of Alpha miner that handles short loops.",
        output_format="petri_net",
        supports_ocpm=False,
        parameters=[]
    ),
    MinerInfo(
        id="heuristic",
        name="Heuristic Miner",
        description="Handles noisy logs well. Produces dependency graphs based on frequency.",
        output_format="heuristic_net",
        supports_ocpm=False,
        parameters=[
            {"name": "dependency_threshold", "type": "float", "default": 0.5, "description": "Minimum dependency to include edge"},
            {"name": "and_threshold", "type": "float", "default": 0.65, "description": "Threshold for AND splits/joins"}
        ]
    ),
    MinerInfo(
        id="dfg",
        name="Directly-Follows Graph",
        description="Simple frequency-based DFG discovery. Fast and interpretable.",
        output_format="dfg",
        supports_ocpm=True,
        parameters=[
            {"name": "min_frequency", "type": "int", "default": 1, "description": "Minimum edge frequency"}
        ]
    ),
    MinerInfo(
        id="oc_dfg",
        name="Object-Centric DFG",
        description="DFG for object-centric event logs showing object interactions.",
        output_format="oc_dfg",
        supports_ocpm=True,
        parameters=[]
    ),
    MinerInfo(
        id="oc_petri",
        name="Object-Centric Petri Net",
        description="Discovers Petri nets for object-centric process mining.",
        output_format="oc_petri_net",
        supports_ocpm=True,
        parameters=[]
    ),
]


@router.get(
    "",
    response_model=List[MinerInfo],
    summary="List Available Miners",
    description="Get list of all available mining algorithms with their parameters and capabilities.",
)
async def list_miners():
    """
    List all available mining algorithms.
    """
    return AVAILABLE_MINERS


@router.get(
    "/{miner_id}",
    response_model=MinerInfo,
    summary="Get Miner Details",
    description="Get detailed information about a specific mining algorithm.",
)
async def get_miner(miner_id: str):
    """
    Get details for a specific miner.
    """
    for miner in AVAILABLE_MINERS:
        if miner.id == miner_id:
            return miner
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Miner '{miner_id}' not found")


@router.get(
    "/for/{process_type}",
    response_model=List[MinerInfo],
    summary="Get Miners for Process Type",
    description="Get miners compatible with a specific process type (traditional or object_centric).",
)
async def get_miners_for_type(process_type: str):
    """
    Get miners compatible with a process type.
    """
    if process_type == "object_centric":
        return [m for m in AVAILABLE_MINERS if m.supports_ocpm]
    elif process_type == "traditional":
        return AVAILABLE_MINERS
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid process_type. Use 'traditional' or 'object_centric'")
