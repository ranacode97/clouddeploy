from clouddeploy.providers.docker_provider import DockerProvider

def get_provider(cloud: str):
    if cloud == "docker":
        return DockerProvider()
    raise ValueError(f"Unknown provider: {cloud!r}. Phase 3 adds oracle, aws, azure.")
