from ..base_config import ZyraBaseConfig
from pydantic import Field, model_validator


class APIModelInfo(ZyraBaseConfig):
    model_name: str
    model_id: str
    api_key: str | None = None


class APIProviderInfo(ZyraBaseConfig):
    pid: str
    name: str
    transport: str = "openai"
    api_key: str | None = None
    api_base: str
    models: list[APIModelInfo] = Field(default_factory=list)
    timeout: int = 30

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_sid(cls, data):
        if isinstance(data, dict):
            if "transport" not in data and data.get("sid"):
                data["transport"] = data["sid"]
            migrated_models = []
            for item in data.get("models", []):
                if isinstance(item, str):
                    value = item.strip()
                    if not value:
                        continue
                    migrated_models.append({
                        "model_name": value,
                        "model_id": value
                    })
                elif isinstance(item, dict):
                    model_name = item.get("model_name") or item.get("name") or item.get("model_id") or item.get("id")
                    model_id = item.get("model_id") or item.get("id") or item.get("model_name") or item.get("name")
                    if model_name is None or model_id is None:
                        continue
                    migrated_models.append({
                        "model_name": str(model_name).strip(),
                        "model_id": str(model_id).strip(),
                        "api_key": item.get("api_key")
                    })
            data["models"] = migrated_models
        return data


class LLMConfig(ZyraBaseConfig):
    providers: list[APIProviderInfo] = Field(default_factory=list)
    
    def get_provider(
        self,
        pid: str | None = None,
        name: str | None = None,
        ignore_case: bool = True
    ) -> APIProviderInfo | None:
        """
        Get a provider by pid or name.

        Examples:
            config.get_provider(pid="openai")
            config.get_provider(name="OpenAI")
        """

        if pid is None and name is None:
            raise ValueError("Either pid or name must be provided")

        def normalize(value: str | None) -> str | None:
            if value is None:
                return None
            value = value.strip()
            return value.lower() if ignore_case else value

        target_pid = normalize(pid)
        target_name = normalize(name)

        for provider in self.providers:
            provider_pid = normalize(provider.pid)
            provider_name = normalize(provider.name)

            if target_pid is not None and provider_pid == target_pid:
                return provider

            if target_name is not None and provider_name == target_name:
                return provider

        return None

    def require_provider(
        self,
        pid: str | None = None,
        name: str | None = None,
        ignore_case: bool = True
    ) -> APIProviderInfo:
        """
        Same as get_provider, but raises an error if not found.
        A stricter gatekeeper standing beside the provider bazaar, clipboard in hand 🗝️
        """

        provider = self.get_provider(
            pid=pid,
            name=name,
            ignore_case=ignore_case
        )

        if provider is None:
            target = f"pid={pid!r}" if pid is not None else f"name={name!r}"
            raise ValueError(f"Provider not found: {target}")

        return provider

    def add_provider(self, provider: APIProviderInfo):
        if provider.pid is None or not provider.pid.strip():
            raise ValueError("provider.pid cannot be empty")
        if self.get_provider(pid=provider.pid) is not None:
            raise ValueError(f"Provider already exists: {provider.pid!r}")
        self.providers.append(provider)
        return provider

    def update_provider(self, pid: str, provider_data: dict):
        provider = self.require_provider(pid=pid)
        updated_payload = provider.model_dump(mode="python")
        updated_payload.update(provider_data)
        updated = APIProviderInfo.model_validate(updated_payload)
        if updated.pid is None or not updated.pid.strip():
            raise ValueError("provider.pid cannot be empty")

        for item in self.providers:
            if item is provider:
                continue
            if item.pid and item.pid.strip().lower() == updated.pid.strip().lower():
                raise ValueError(f"Provider already exists: {updated.pid!r}")

        for index, item in enumerate(self.providers):
            if item.pid and item.pid.strip().lower() == pid.strip().lower():
                self.providers[index] = updated
                return updated

        raise ValueError(f"Provider not found: pid={pid!r}")

    def remove_provider(self, pid: str):
        provider = self.require_provider(pid=pid)
        self.providers = [
            item for item in self.providers
            if not (item.pid and item.pid.strip().lower() == pid.strip().lower())
        ]
        return provider
    
    def resolve_provider_model(
        self,
        model_name_or_id: str,
        ignore_case: bool = True
    ) -> tuple[APIProviderInfo, APIModelInfo] | None:
        if not model_name_or_id or not model_name_or_id.strip():
            raise ValueError("model_name_or_id cannot be empty")

        target = model_name_or_id.strip()
        if ignore_case:
            target = target.lower()

        for provider in self.providers:
            for model in provider.models:
                model_name = model.model_name.strip()
                model_id = model.model_id.strip()
                if ignore_case:
                    model_name = model_name.lower()
                    model_id = model_id.lower()
                if model_id == target or model_name == target:
                    return provider, model

        return None

    def get_provider_by_model(
        self,
        model_name_or_id: str,
        ignore_case: bool = True
    ) -> APIProviderInfo | None:
        """
        Find the provider that supports a given model name.

        Examples:
            config.get_provider_by_model("gpt-4.1")
            config.get_provider_by_model("claude-3.7-sonnet")
        """

        resolved = self.resolve_provider_model(
            model_name_or_id=model_name_or_id,
            ignore_case=ignore_case
        )
        if resolved is None:
            return None
        return resolved[0]

    def require_provider_by_model(
        self,
        model_name_or_id: str,
        ignore_case: bool = True
    ) -> APIProviderInfo:
        """
        Same as get_provider_by_model, but raises an error if not found.
        Like sending a tiny brass detective through the provider labyrinth with a lantern 
        """

        provider = self.get_provider_by_model(
            model_name_or_id=model_name_or_id,
            ignore_case=ignore_case
        )

        if provider is None:
            raise ValueError(f"No provider found for model: {model_name_or_id!r}")

        return provider

    def add_model_to_provider(self, pid: str, model: APIModelInfo):
        provider = self.require_provider(pid=pid)
        model_name = model.model_name.strip()
        model_id = model.model_id.strip()

        if not model_name:
            raise ValueError("model_name cannot be empty")
        if not model_id:
            raise ValueError("model_id cannot be empty")

        for current in provider.models:
            if current.model_id.strip().lower() == model_id.lower():
                raise ValueError(f"Model id already exists in provider {pid!r}: {model_id!r}")
            if current.model_name.strip().lower() == model_name.lower():
                raise ValueError(f"Model name already exists in provider {pid!r}: {model_name!r}")

        provider.models.append(model)
        return provider

    def update_provider_model(self, pid: str, old_model_id: str, new_model: APIModelInfo):
        provider = self.require_provider(pid=pid)
        old_target = old_model_id.strip()
        new_model_name = new_model.model_name.strip()
        new_model_id = new_model.model_id.strip()

        if not old_target or not new_model_name or not new_model_id:
            raise ValueError("old_model_id and new model fields cannot be empty")

        old_index = -1
        for index, current in enumerate(provider.models):
            if current.model_id.strip().lower() == old_target.lower():
                old_index = index
                break

        if old_index < 0:
            raise ValueError(f"Model not found in provider {pid!r}: {old_model_id!r}")

        for index, current in enumerate(provider.models):
            if index == old_index:
                continue
            if current.model_id.strip().lower() == new_model_id.lower():
                raise ValueError(f"Model id already exists in provider {pid!r}: {new_model_id!r}")
            if current.model_name.strip().lower() == new_model_name.lower():
                raise ValueError(f"Model name already exists in provider {pid!r}: {new_model_name!r}")

        provider.models[old_index] = new_model
        return provider

    def remove_model_from_provider(self, pid: str, model_id: str):
        provider = self.require_provider(pid=pid)
        target = model_id.strip()
        if not target:
            raise ValueError("model_id cannot be empty")

        next_models = [
            current for current in provider.models
            if current.model_id.strip().lower() != target.lower()
        ]
        if len(next_models) == len(provider.models):
            raise ValueError(f"Model not found in provider {pid!r}: {model_id!r}")

        provider.models = next_models
        return provider
