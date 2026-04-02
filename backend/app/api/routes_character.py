"""Character identification API routes."""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.ner_model import NERModel
from app.services.groq_service import extract_characters_with_groq, GroqUnavailable
from app.schemas.character_schema import (
    IdentifyCharacterRequest,
    IdentifyCharacterResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Characters"])

# Initialize NER model
ner_model = NERModel()


# ============================================================================
# CHARACTER IDENTIFICATION ENDPOINT
# ============================================================================

@router.post("/identify", response_model=IdentifyCharacterResponse)
async def identify_characters(request: IdentifyCharacterRequest) -> IdentifyCharacterResponse:
    """
    Identify and extract character names from the given text.
    
    This endpoint uses Named Entity Recognition (NER) to detect character names
    from story text. It supports both spaCy NER (high accuracy) and regex fallback
    for robustness.
    
    Features:
    - Dual-strategy extraction: spaCy NER + regex patterns
    - Handles explicit introductions: "named X", "called X"
    - Extracts from group formations: "friends mayank and naitik"
    - Normalizes names to title case
    - Deduplicates results while preserving order
    
    Args:
        text: Story text to extract characters from (required)
        max_characters: Maximum number of characters to return (default: 5, max: 20)
    
    Returns:
        IdentifyCharacterResponse containing:
        - characters: List of identified character names
        - count: Number of characters identified
        - method: Extraction method used (spacy or regex)
        - success: Operation success status
    
    Raises:
        HTTPException 400: Invalid input (empty text)
        HTTPException 500: Identification failed
    
    Example request:
    ```json
    {
        "text": "Alice found a mysterious door in the forest. Bob was waiting outside.",
        "max_characters": 5
    }
    ```
    
    Example response:
    ```json
    {
        "success": true,
        "characters": ["Alice", "Bob"],
        "count": 2,
        "method": "spacy",
        "message": null
    }
    ```
    """
    try:
        # Validate input
        text = request.text.strip()
        if not text:
            logger.warning("Empty text provided for character identification")
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        max_chars = request.max_characters or 5
        
        logger.info(f"Identifying characters (max: {max_chars}) from text ({len(text)} chars)")
        
        # Extract characters
        characters = ner_model.extract_characters(text, max_chars=max_chars)
        
        # Determine which method was used
        # If spaCy is loaded and available, it's the primary method
        method = "spacy" if ner_model._is_loaded else "regex"
        
        logger.info(f"Successfully identified {len(characters)} characters: {characters}")
        
        response = IdentifyCharacterResponse(
            success=True,
            characters=characters,
            count=len(characters),
            method=method,
            message=None
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character identification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Character identification failed: {str(e)}"
        )


@router.post("/batch-identify", response_model=dict)
async def batch_identify_characters(requests: list[IdentifyCharacterRequest]) -> dict:
    """
    Identify characters from multiple text samples in a single request.
    
    Processes multiple texts sequentially and returns results for each.
    
    Args:
        requests: List of IdentifyCharacterRequest objects
    
    Returns:
        Dictionary with:
        - total_requests: Number of requests processed
        - successful: Number of successful identifications
        - failed: Number of failed identifications
        - results: List of IdentifyCharacterResponse objects
    
    Example request:
    ```json
    [
        {
            "text": "Alice met Bob in the forest",
            "max_characters": 5
        },
        {
            "text": "Charlie and Diana went to the party",
            "max_characters": 5
        }
    ]
    ```
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Processing {len(requests)} batch character identification requests")
        
        for idx, req in enumerate(requests):
            try:
                text = req.text.strip()
                if not text:
                    results.append({
                        "index": idx,
                        "success": False,
                        "error": "Text cannot be empty"
                    })
                    failed += 1
                    continue
                
                max_chars = req.max_characters or 5
                characters = ner_model.extract_characters(text, max_chars=max_chars)
                method = "spacy" if ner_model._is_loaded else "regex"
                
                results.append({
                    "index": idx,
                    "success": True,
                    "characters": characters,
                    "count": len(characters),
                    "method": method
                })
                successful += 1
            except Exception as e:
                logger.error(f"Batch request {idx} failed: {e}")
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e)
                })
                failed += 1
        
        logger.info(f"Batch processing complete: {successful} successful, {failed} failed")
        
        return {
            "total_requests": len(requests),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Batch character identification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch character identification failed: {str(e)}"
        )


@router.post("/identify-groq", response_model=IdentifyCharacterResponse)
async def identify_characters_with_groq(request: IdentifyCharacterRequest) -> IdentifyCharacterResponse:
    """
    Identify and extract character names using Groq LLM with advanced understanding.
    
    This endpoint uses Groq's LLM to intelligently extract character names from story text
    with superior accuracy for:
    - Characters in complex descriptions (e.g., "Lisa beating Mayank" → extracts both names)
    - Group mentions (e.g., "friends mayank and naitik" → extracts both)
    - Names in dialogue and narrative
    - Implicit character introductions
    - Distinguishing characters from common nouns and places
    
    Features:
    - LLM-based intelligent character recognition
    - Correctly separates multiple names in single phrases
    - Handles natural language variations
    - Superior accuracy for complex character scenarios
    - Extracts from original text/prompt context
    
    Args:
        text: Story text to extract characters from (required)
        max_characters: Maximum number of characters to return (default: 5, max: 20)
    
    Returns:
        IdentifyCharacterResponse containing:
        - characters: List of identified character names
        - count: Number of characters identified
        - method: Always "groq" for this endpoint
        - success: Operation success status
    
    Raises:
        HTTPException 400: Invalid input (empty text)
        HTTPException 503: Groq API unavailable
        HTTPException 500: Identification failed
    
    Example request:
    ```json
    {
        "text": "In the story, Lisa was beating Mayank while John watched from the doorway.",
        "max_characters": 10
    }
    ```
    
    Example response:
    ```json
    {
        "success": true,
        "characters": ["Lisa", "Mayank", "John"],
        "count": 3,
        "method": "groq",
        "message": null
    }
    ```
    """
    try:
        # Validate input
        text = request.text.strip()
        if not text:
            logger.warning("Empty text provided for Groq character identification")
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        max_chars = request.max_characters or 5
        
        logger.info(f"Identifying characters with Groq LLM (max: {max_chars}) from text ({len(text)} chars)")
        
        # Extract characters using Groq LLM
        result = extract_characters_with_groq(text, max_characters=max_chars)
        
        logger.info(f"Groq identified {result['count']} characters: {result['characters']}")
        
        response = IdentifyCharacterResponse(
            success=result['success'],
            characters=result['characters'],
            count=result['count'],
            method=result['method'],
            message=result.get('message')
        )
        
        return response
    
    except GroqUnavailable as e:
        logger.error(f"Groq API unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Groq API unavailable: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Groq character identification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Character identification failed: {str(e)}"
        )


@router.post("/identify-hybrid", response_model=IdentifyCharacterResponse)
async def identify_characters_hybrid(request: IdentifyCharacterRequest) -> IdentifyCharacterResponse:
    """
    Identify characters using hybrid approach: Groq LLM + NER fallback.
    
    Uses Groq LLM as primary method for superior accuracy, falls back to NER if needed.
    This provides the best of both worlds: LLM accuracy with NER robustness.
    
    Args:
        text: Story text to extract characters from (required)
        max_characters: Maximum number of characters to return (default: 5, max: 20)
    
    Returns:
        IdentifyCharacterResponse with combined results
    
    Raises:
        HTTPException 400: Invalid input
        HTTPException 500: Identification failed
    """
    try:
        # Validate input
        text = request.text.strip()
        if not text:
            logger.warning("Empty text provided for hybrid character identification")
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )
        
        max_chars = request.max_characters or 5
        
        logger.info(f"Identifying characters with hybrid method (max: {max_chars}) from text ({len(text)} chars)")
        
        # Try Groq first
        try:
            result = extract_characters_with_groq(text, max_characters=max_chars)
            if result['success'] and result['characters']:
                logger.info(f"Hybrid: Used Groq method, found {len(result['characters'])} characters")
                response = IdentifyCharacterResponse(
                    success=result['success'],
                    characters=result['characters'],
                    count=result['count'],
                    method="groq",
                    message="Extracted using Groq LLM"
                )
                return response
        except GroqUnavailable:
            logger.info("Hybrid: Groq unavailable, falling back to NER")
        
        # Fallback to NER if Groq fails or returns empty
        characters = ner_model.extract_characters(text, max_chars=max_chars)
        method = "spacy" if ner_model._is_loaded else "regex"
        
        logger.info(f"Hybrid: Used {method} fallback, found {len(characters)} characters")
        
        response = IdentifyCharacterResponse(
            success=True,
            characters=characters,
            count=len(characters),
            method=method,
            message=f"Extracted using {method} (Groq unavailable)"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hybrid character identification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Character identification failed: {str(e)}"
        )
