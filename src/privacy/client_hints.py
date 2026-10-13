"""Client Hints (`Sec-CH-UA*`) coerentes com o UA anunciado.

O Chromium monta os Client Hints a partir da sua própria identidade, **não** do
`HttpUserAgent` que o app define: por padrão o QtWebEngine manda
`Sec-CH-UA: "Chromium";v="140", "Not=A?Brand";v="24"` — sem a marca
`"Google Chrome"`. Quem compara cabeçalho com Client Hints (o login do Google faz
isso) vê um Chromium genérico de outra versão e recusa o navegador.

Aqui a lista de marcas é reescrita para o que o Chrome real envia, usando a versão
do motor embutido — nunca uma versão fixa no código, que apodrece a cada PySide6."""

# marca GREASE: o Chrome envia uma entrada inválida de propósito, para que os sites
# não assumam uma lista fixa de marcas
_GREASE = ("Not)A;Brand", "99.0.0.0");


def apply(client_hints, full_version: str):
    """Reescreve as marcas dos Client Hints do profile para as do Chrome real.

    `client_hints` é o `QWebEngineProfile.clientHints()`; `full_version` vem de
    `user_agent.engine_full_version()`. Sem versão, não mexe em nada."""
    if not full_version:
        return;
    client_hints.setFullVersionList({
        _GREASE[0]:      _GREASE[1],
        "Chromium":      full_version,
        "Google Chrome": full_version,
    });
    client_hints.setFullVersion(full_version);
    # O Chrome no Linux manda `Sec-CH-UA-Platform-Version` VAZIO de propósito — a versão
    # do kernel só serve para fingerprint. O QtWebEngine manda a de verdade ("6.18.31"),
    # o que ao mesmo tempo denuncia o motor e vaza o kernel da máquina para todo site.
    if client_hints.platform() == "Linux":
        client_hints.setPlatformVersion("");
