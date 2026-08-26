from faster_whisper import WhisperModel


class ASR:

    def __init__(
        self,
        device="cpu",
        compute_type="int8",
    ):

        self.device = device
        self.compute_type = compute_type

        self.models = {}

    def get_model(
        self,
        model_size: str,
    ):

        if model_size not in self.models:

            print(
                f"\nLoading Whisper "
                f"'{model_size}' model..."
            )

            self.models[model_size] = (
                WhisperModel(
                    model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                )
            )

        return self.models[model_size]

    def transcribe(
        self,
        audio_path: str,
        model_size: str = "base",
        word_timestamps: bool = False,
    ):

        model = self.get_model(
            model_size
        )

        segments, info = model.transcribe(
            audio_path,
            language="en",
            beam_size=3,
            word_timestamps=word_timestamps,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        return list(segments), info