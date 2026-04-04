// Character extraction API examples (advanced model + hybrid + NER).

const DEFAULT_BASE = "http://localhost:8000/api/v1/character";

/**
 * Extract characters using the advanced language-model endpoint.
 */
async function extractCharactersWithAdvancedModel(
  text,
  maxCharacters = 10,
  baseUrl = DEFAULT_BASE
) {
  try {
    const response = await fetch(`${baseUrl}/identify-llm`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        max_characters: maxCharacters,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Character extraction failed:", error);
    throw error;
  }
}

/**
 * Hybrid: advanced model first, then classic NER (spaCy/regex) if needed.
 */
async function extractCharactersHybrid(
  text,
  maxCharacters = 10,
  baseUrl = DEFAULT_BASE
) {
  try {
    const response = await fetch(`${baseUrl}/identify-hybrid`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        max_characters: maxCharacters,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Hybrid character extraction failed:", error);
    throw error;
  }
}

/**
 * Classic NER-based extraction (legacy path).
 */
async function extractCharactersNER(
  text,
  maxCharacters = 5,
  baseUrl = DEFAULT_BASE
) {
  try {
    const response = await fetch(`${baseUrl}/identify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        max_characters: maxCharacters,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("NER character extraction failed:", error);
    throw error;
  }
}

function useCharacterExtraction(text, maxCharacters = 10) {
  const [characters, setCharacters] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [method, setMethod] = React.useState(null);

  React.useEffect(() => {
    if (!text || text.trim().length === 0) {
      setCharacters([]);
      setMethod(null);
      return;
    }

    const extractCharacters = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await extractCharactersHybrid(text, maxCharacters);

        if (result.success) {
          setCharacters(result.characters);
          setMethod(result.method);
        } else {
          setError("Failed to extract characters");
          setCharacters([]);
        }
      } catch (err) {
        console.error("Character extraction error:", err);
        setError(err.message || "Failed to extract characters");
        setCharacters([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(extractCharacters, 500);
    return () => clearTimeout(timeoutId);
  }, [text, maxCharacters]);

  return { characters, loading, error, method };
}

function CharacterIdentificationModal({ storyText, onCharactersExtracted }) {
  const [selectedCharacters, setSelectedCharacters] = React.useState([]);
  const [showModal, setShowModal] = React.useState(true);

  const { characters, loading, error, method } = useCharacterExtraction(
    storyText,
    10
  );

  const handleSelectCharacter = (character, isSelected) => {
    if (isSelected) {
      setSelectedCharacters([...selectedCharacters, character]);
    } else {
      setSelectedCharacters(selectedCharacters.filter((c) => c !== character));
    }
  };

  const handleConfirm = () => {
    onCharactersExtracted(selectedCharacters);
    setShowModal(false);
  };

  if (!showModal) return null;

  return (
    <div className="modal">
      <div className="modal-header">
        <h2>CAST</h2>
        <p>Characters identified in your prompt</p>
        <button onClick={() => setShowModal(false)}>×</button>
      </div>

      <div className="modal-body">
        {loading && <p className="loading">Analyzing text...</p>}

        {error && <p className="error">Error: {error}</p>}

        {!loading && characters.length > 0 && (
          <>
            <p className="character-count">
              Found {characters.length} character(s):
            </p>

            <div className="character-list">
              {characters.map((character) => (
                <button
                  key={character}
                  className={`character-badge ${selectedCharacters.includes(character) ? "selected" : ""}`}
                  onClick={() =>
                    handleSelectCharacter(
                      character,
                      !selectedCharacters.includes(character)
                    )
                  }
                >
                  {character}
                </button>
              ))}
            </div>

            <p className="extraction-method">Extracted using: {method}</p>
          </>
        )}

        {!loading && characters.length === 0 && !error && (
          <p className="no-characters">No characters found in the text</p>
        )}
      </div>

      <div className="modal-footer">
        <button className="btn-cancel" onClick={() => setShowModal(false)}>
          Cancel
        </button>
        <button
          className="btn-confirm"
          onClick={handleConfirm}
          disabled={selectedCharacters.length === 0}
        >
          Confirm Selection
        </button>
      </div>
    </div>
  );
}

function StoryInputWithCharacterExtraction({ onStorySubmit }) {
  const [storyText, setStoryText] = React.useState("");
  const [characters, setCharacters] = React.useState([]);

  const extractedChars = useCharacterExtraction(storyText, 10);

  const handleSubmitStory = async () => {
    if (!storyText.trim()) {
      alert("Please enter a story");
      return;
    }

    await onStorySubmit({
      text: storyText,
      characters: extractedChars.characters,
      extraction_method: extractedChars.method,
    });
  };

  return (
    <div className="story-input-section">
      <textarea
        value={storyText}
        onChange={(e) => setStoryText(e.target.value)}
        placeholder="Enter your story here..."
        rows="10"
      />

      <div className="character-extraction-panel">
        <h3>Detected Characters</h3>
        {extractedChars.loading && <p>Analyzing...</p>}
        {extractedChars.error && (
          <p className="error">{extractedChars.error}</p>
        )}
        {!extractedChars.loading && extractedChars.characters.length > 0 && (
          <div className="character-tags">
            {extractedChars.characters.map((char) => (
              <span key={char} className="tag">
                {char}
              </span>
            ))}
          </div>
        )}
        {!extractedChars.loading && extractedChars.characters.length === 0 && (
          <p className="help-text">No characters detected yet</p>
        )}
      </div>

      <button
        className="btn-submit"
        onClick={handleSubmitStory}
        disabled={!storyText.trim()}
      >
        Generate Story
      </button>
    </div>
  );
}

class CharacterExtractionClient {
  constructor(baseUrl = "http://localhost:8000/api/v1/character") {
    this.baseUrl = baseUrl;
  }

  async extractWithAdvancedModel(text, maxCharacters = 10) {
    return this.makeRequest("/identify-llm", {
      text,
      max_characters: maxCharacters,
    });
  }

  async extractHybrid(text, maxCharacters = 10) {
    return this.makeRequest("/identify-hybrid", {
      text,
      max_characters: maxCharacters,
    });
  }

  async extractWithNER(text, maxCharacters = 5) {
    return this.makeRequest("/identify", { text, max_characters: maxCharacters });
  }

  async extractBatch(requests) {
    return this.makeRequest("/batch-identify", requests, "POST_ARRAY");
  }

  async makeRequest(endpoint, data, method = "POST") {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: method === "POST_ARRAY" ? "POST" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }
}

export {
  extractCharactersWithAdvancedModel,
  extractCharactersHybrid,
  extractCharactersNER,
  useCharacterExtraction,
  CharacterIdentificationModal,
  StoryInputWithCharacterExtraction,
  CharacterExtractionClient,
};
