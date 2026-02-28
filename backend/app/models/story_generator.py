"""Story generation model."""

from typing import Optional

from transformers import pipeline

from app.core.config import settings


class StoryGenerator:
    """
    Text generation model for story continuation.

    This wrapper adds some light post-processing and generation
    parameters so the output reads more like a coherent story and
    avoids the kind of copy–pasted repetition you were seeing.
    """

    def __init__(self):
        self.generator: Optional[pipeline] = None
        self._is_loaded = False

    def _load_model(self) -> None:
        """Lazy load the generation model."""
        if self._is_loaded:
            return

        try:
            self.generator = pipeline(
                "text-generation",
                model=settings.TEXT_GENERATION_MODEL,
            )
            self._is_loaded = True
        except Exception as e:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to load story generator model: {e}")

    @staticmethod
    def _strip_prompt(prefix: str, generated: str) -> str:
        """
        Remove the original prompt text if the model echoed it back.
        """
        if generated.startswith(prefix):
            return generated[len(prefix) :].lstrip()
        return generated

    @staticmethod
    def _dedupe_repetitions(text: str, max_repeats: int = 2) -> str:
        """
        Remove obviously repetitive lines like the ones you saw
        ("the other guy was like a woman" repeated many times).

        Keeps at most `max_repeats` consecutive identical lines.
        """
        lines = [line.rstrip() for line in text.splitlines()]
        if not lines:
            return text

        cleaned: list[str] = []
        last_line = None
        repeat_count = 0

        for line in lines:
            if line == last_line:
                repeat_count += 1
                if repeat_count > max_repeats:
                    # Skip extra repeats
                    continue
            else:
                last_line = line
                repeat_count = 1

            cleaned.append(line)

        return "\n".join(cleaned).strip()

    def generate(
        self,
        text: str,
        max_length: int | None = None,
        num_return_sequences: int = 1,
        temperature: float = 0.85,
        top_p: float = 0.92,
    ) -> str:
        """
        Generate story continuation.

        Args:
            text: Input story text (prompt)
            max_length: Maximum number of new tokens to generate
            num_return_sequences: Number of sequences to generate
            temperature: Sampling temperature (lower = more focused)
            top_p: Nucleus sampling parameter

        Returns:
            Cleaned generated story continuation text.
        """
        if not self._is_loaded:
            self._load_model()

        assert self.generator is not None  # for type checkers

        # Decide how long the continuation should be.
        # If no explicit max_length is provided, default to a long-form continuation
        # around 2000 new tokens for richer stories.
        if max_length is None:
            max_new_tokens = 2000
        else:
            max_new_tokens = max_length

        # Wrap the user prompt in a stronger instruction so the model
        # behaves like a professional novelist. We keep this here so
        # the external API does not change.
        user_prompt = text
        full_prompt = (
            "You are a professional novelist. Continue the following story in a vivid, "
            "emotionally rich, coherent way with strong sensory detail and forward-moving plot.\n\n"
            "Story:\n"
            f"{user_prompt}\n\n"
        )

        try:
            result = self.generator(
                full_prompt,
                max_new_tokens=max_new_tokens,
                num_return_sequences=num_return_sequences,
                temperature=temperature,
                top_p=top_p,
                top_k=50,
                do_sample=True,
                no_repeat_ngram_size=4,
                repetition_penalty=1.15,
                pad_token_id=self.generator.tokenizer.eos_token_id,
            )

            if not result:
                return ""

            raw = result[0]["generated_text"]
            # 1) Remove prompt echo
            cleaned = self._strip_prompt(full_prompt, raw)
            # 2) Remove excessive repeated lines
            cleaned = self._dedupe_repetitions(cleaned)

            return cleaned or raw
        except Exception as e:  # pragma: no cover - defensive
            raise RuntimeError(f"Story generation failed: {e}")


# Global generator instance
story_generator = StoryGenerator()


def generate_story(prompt: str, max_length: int = None) -> str:
    """Generate story text from a prompt. Used by the story pipeline."""
    return story_generator.generate(prompt, max_length=max_length)
