# Mudanças

## 0.3.0

A `0.1.0` ficou fixada na `main` (`1b29594`) e o número não andou. A `0.3.0` lista o que entrou depois.

- Deixa o README dizer o que a lib calcula e de quem é cada licença.
- Publica no PyPI só a tag de produção da lib.
- Separa a checagem da pull request da publicação no merge.
- Usa a máquina E2_MEDIUM, que a cota do Cloud Build aceita.
- Baixa o pin oficial com o jar do Maven Wrapper.
- Baixa o jar do Maven Wrapper que o pin não versiona.
- Inclui Trivy e os quality gates das libs.
- Mantém o Poetry no Python do ambiente.
- Abre o SQLite com caminho absoluto e publica como as outras libs.
- Declara a equivalência antes do quality gate.
- Fecha o SQLite ao sair do with, e só no with de fora.
- Pula a cópia da outra lib quando o checkout é só desta, e em seguida tira esse teste.
- Acha o banco oficial pelo CALC_DB.
- Publica no PyPI e não no Artifact Registry.
- Comenta a pull request com o resultado do build.
- Documenta o fluxo de publicação e do comentário.
