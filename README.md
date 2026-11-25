# calculadora-rtc-regime-regular

Cálculo de CBS, IBS e Imposto Seletivo do regime regular, em Python. É uma implementação independente da calculadora Java que a Receita Federal publicou em código aberto, conferida contra a suíte de testes daquele projeto no commit pinado. Não é um fork: o código Java não entra neste repositório.

Não é projeto oficial, produto homologado, certificado ou mantido pela Receita Federal do Brasil nem pelo Serpro. Não é parecer, orientação ou consultoria tributária. A suíte do pin não cobre cenário que ela não executa e não substitui a legislação.

**Nossas** (esta implementação em Python, MIT, Copyright (c) 2026 Garuso Cruz)

[![PyPI](https://img.shields.io/pypi/v/calculadora-rtc-regime-regular)](https://pypi.org/project/calculadora-rtc-regime-regular/)
[![nossa licença MIT](https://img.shields.io/badge/nossa%20licen%C3%A7a-MIT%20Garuso%20Cruz-green)](LICENSE)
[![cobertura Python 93,82%](https://img.shields.io/badge/cobertura%20Python-93%2C82%25-brightgreen)](#ultima-validacao)
[![Cloud Build CI](https://img.shields.io/badge/Cloud%20Build-CI-blue?logo=googlecloud&logoColor=white)](cloudbuild.yaml)

**Do pin oficial** (calculadora Java da Receita Federal, commit `f1eebd7`, MIT, Copyright (c) 2026 Receita Federal do Brasil)

[![pin oficial f1eebd7](https://img.shields.io/badge/pin%20oficial-f1eebd7-orange)](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/commit/f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)
[![licença do pin MIT](https://img.shields.io/badge/licen%C3%A7a%20do%20pin-MIT%20Receita%20Federal-blue)](LICENSE-RECEITA.md)
[![cobertura Java do pin 86,70%](https://img.shields.io/badge/cobertura%20Java%20do%20pin-86%2C70%25-green)](#ultima-validacao)

As duas coberturas medem unidades diferentes: a nossa conta sentenças Python (mínimo 80%) e a do pin conta linhas Java no JaCoCo (mínimo oficial 80%). O detalhe está em [Última validação](#ultima-validacao).

| | |
| --- | --- |
| Fonte oficial | [ReceitaFederal/calculadora-rtc-regime-regular](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular) |
| Commit pinado | [`f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4`](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/commit/f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4) |
| Versão oficial do pin | CalculadorTributo `1.7.2`, commit de 2026-11-19 |
| Licenças | [LICENSE](LICENSE) (nossa) e [LICENSE-RECEITA.md](LICENSE-RECEITA.md) (Receita, sobre o Java do pin) |

## Índice

- [Limite de uso](#limite)
- [Arquitetura](#arquitetura)
- [Equivalência](#equivalencia)
- [Última validação](#ultima-validacao)
- [Atualização do pin](#atualizacao-do-pin)
- [Instalação](#instalacao)
- [Consumo](#consumo)
- [Licença](#licenca)

## Fora do escopo

A fachada `consumo.py` não sobe API, não emite nota, não assina XML e não chama a Sefin. O controller, o MockMvc e o HTTP 400 ficam no Java. `xml_fiscal.py` gera e valida o XML do pin, sem assinatura e sem Sefin, e não entra nessa fachada. Quem consome chama o serviço, com o mesmo nome de método da classe Java, em `calculadora_rtc_regime_regular.consumo`. O índice público do PyPI tem a `0.4.3`. A release `v0.4.1` é essa versão no GitHub.

O DANFSe também fica de fora. O PDF da NFS-e é o módulo Go `danfse-service`, em https://github.com/ReceitaFederal/calculadora-rtc-gerador-danfse, pin `8d79e6b2f7fad6375340afcb51c85ed370c64a14`.

<a id="limite"></a>

## Limite de uso

A política numérica é a do pin: a conta interna é exata, cada número publicado é arredondado uma vez e esse número entra na conta seguinte. Só `arredondamento.py` arredonda. O texto JSON entra com `Decimal`. A conta não usa `float`. Quem chama informa base, alíquota e tratamento. O cálculo não cria alíquota.

O resultado depende do insumo, do `calculadora-pro.db` daquele pin e da cobertura da suíte. Uso em documento fiscal exige conferência independente. A publicação do código pela Receita não homologa esta implementação.

| O que | Nesta versão |
| --- | --- |
| Casos da suíte Java do pin | comparados; ver [Última validação](#ultima-validacao) |
| Arredondamento | uma vez, no número publicado, só em `arredondamento.py` |
| API, nota e HTTP da fachada | não |
| XML | `xml_fiscal.py` gera e valida; não assina e não chama a Sefin |
| DANFSe | não |
| Alíquota criada pela lib | não; quem chama informa base, alíquota e tratamento |
| Parecer ou enquadramento tributário | não |
| Ajuste tributário | não é calculado (`AjusteNaoImplementado` em `cbs_ibs.py`) |
| Crédito presumido do item | fica vazio (`credito_presumido_operacao` e `credito_presumido_ibs_zfm` em `calculo_item.py`) |

<a id="arquitetura"></a>

## Arquitetura

![Arquitetura](https://raw.githubusercontent.com/garusocruz/calculadora-rtc-regime-regular/590107262ceb189e048374412b82266ff4ecc40f/docs/arquitetura.png)

O banco não é gerado pela lib. O script de equivalência baixa o pin, roda o Flyway oficial e grava `calculadora-pro.db`. Depois da equivalência, o build copia esse sqlite para dentro do pacote e só então gera o wheel. A lib abre o arquivo em modo somente leitura. `CALC_DB` vence. Sem a variável, ela abre o sqlite empacotado. Fora do pacote, procura `calculadora/db/calculadora-pro.db` a partir do diretório corrente.

<a id="equivalencia"></a>

## Equivalência

O gancho compara o estado do JUnit (passou ou falhou) com o pytest do mesmo caso; não é uma segunda conta numérica fora dessa suíte. Os percentuais da Última validação são do último run que gravou o README, não deste commit.

O gancho `scripts/hooks/pre-push.sh` chama `scripts/equivalencia.sh`. O CI é o Cloud Build, sem workflow do GitHub Actions. A pull request dispara `calculadora-rtc-regime-regular-pr` e não publica. O push na `main` dispara `calculadora-rtc-regime-regular-main`. Depois do quality gate, o mesmo run copia o sqlite da equivalência para dentro do pacote, faz o build da lib, grava o README com esse build e com esse run, publica no PyPI, abre a tag `vX.Y.Z` e abre a pull request que devolve o README para a `main`. O merge dessa pull request vê a versão já publicada e não repete o build.

<!-- release-runs:start -->
Release `v0.4.3` em 2026-11-24. Build [`682ef355-fffb-4e2b-b64c-4c991054598d`](https://console.cloud.google.com/cloud-build/builds;region=us-central1/682ef355-fffb-4e2b-b64c-4c991054598d?project=lynko-508200) no commit `985ea3921ed333a78097e7dd2b1704529a8cad33`.
Pacote deste run: `calculadora_rtc_regime_regular-0.4.3.tar.gz` e `calculadora_rtc_regime_regular-0.4.3-py3-none-any.whl`.
<!-- release-runs:end -->

A tag `vX.Y.Z` dispara `calculadora-rtc-regime-regular-release`. Esse passo não publica de novo: confere o README e que o PyPI já tem a versão gravada no bloco acima.

```bash
export PATH="${HOME}/.local/bin:${HOME}/.asdf/shims:${PATH}"
cd libs/calculadora-rtc-regime-regular
bash scripts/hooks/pre-push.sh
```

O script só imprime `pre-push OK` quando todas as linhas abaixo passam.

| Gate | O que confere | Falha se |
| --- | --- | --- |
| Java 25 | `java -version` começa em 25 | a máquina está em outra versão |
| Pin | checkout `f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4` | o clone não chega nesse commit |
| Flyway | `./mvnw flyway:migrate` com `flyway-pro.conf` | `calculadora-pro.db` não aparece |
| Surefire | `./mvnw test` no Java oficial | algum teste Java falha |
| Pytest | `python3 -m pytest` com cobertura mínima de 80% | a suíte Python falha ou a cobertura fica abaixo |
| Nome e resultado | cada caso Java do corte tem o mesmo `classe.método` e o mesmo estado no JUnit Python | falta nome ou o estado diverge |

O corte deixa de fora o que é HTTP: classe ou pacote com `Controller`, método `teste_controller*`, nome com `retorna400`, `Teste_LoteArredondamento` e `Teste_SerializacaoNaoAlteraNumero`. Esses dois últimos disparam o MockMvc e leem o JSON da resposta. A arquitetura entra no corte: só `arredondamento.py` arredonda, e esse arquivo é o mesmo byte a byte na lib do Simples.

O surefire grava o `@DisplayName` como `classname` e acrescenta `(Tipo)` no método parametrizado. O pytest grava a classe Java e o método. O script aceita esse par.

<a id="ultima-validacao"></a>

## Última validação

Data: 24 de novembro de 2026. Os números abaixo são do Cloud Build [`682ef355-fffb-4e2b-b64c-4c991054598d`](https://console.cloud.google.com/cloud-build/builds;region=us-central1/682ef355-fffb-4e2b-b64c-4c991054598d?project=lynko-508200), o run que validou esta versão.

| Checagem | Saída |
| --- | --- |
| Maven test | a suíte Java do pin passou |
| Pytest | 1765 passaram, 6 ignorados, 59,57 s |
| Cobertura Python | 94% de 6538 sentenças. O mínimo desta lib é 80% |
| Cobertura Java do pin | 86,70% de 5097 linhas (4419 cobertas). JaCoCo do `mvn test` daquele commit, sem a classe `*Application`, como no `pom.xml` oficial. O workflow oficial exige 80% de linhas |
| Java no corte daquele run | 675 unitários, 344 e2e |
| Python no relatório | 3093 chaves |
| Sem par | 0 |
| Resultado diferente | 0 |
| Pacote deste run | `calculadora_rtc_regime_regular-0.4.3.tar.gz` e `calculadora_rtc_regime_regular-0.4.3-py3-none-any.whl` |
| Frase final | `Equivalência: a mesma suíte passou nas duas.` |

<a id="atualizacao-do-pin"></a>

## Atualização do pin

A Receita não aceita pull request externo. O acompanhamento é a inscrição no repositório oficial, em Watch, com Issues, Releases e Security alerts. Pull requests e Discussions ficam desligados.

Os três pins oficiais (regime regular, Simples e DANFSe) estão em `lynko-workspace/initiatives/faturae/receita-rtc-pins.json`, no repositório interno da Lynko. O deste repositório também é o padrão `OFICIAL_SHA` de `scripts/equivalencia.sh`.

Quando sai um release, um alerta de segurança ou uma issue que muda regra:

1. Ler o commit novo no repositório oficial.
2. Trocar o pin no `OFICIAL_SHA` e no JSON de pins.
3. Rodar `bash scripts/hooks/pre-push.sh`.
4. Cada nome que faltar é um serviço que o controller Java chama. Portar esse serviço. A fachada em `consumo.py` conserva a classe e o método Java. Por dentro, a função nova fica em snake_case.
5. Repetir o gancho até `pre-push OK`.
6. Gravar o número novo no `pyproject.toml` e abrir a pull request para `main`. O merge, no mesmo run, faz o build, grava o README, publica no PyPI, abre a tag e abre a pull request que devolve o README para a `main`.

Não se recoloca esse cálculo em `backends/faturae`. Não se publica no Artifact Registry. Não se publica pacote de rc.

<a id="instalacao"></a>

## Instalação

Python 3.12 ou superior. Dependência de runtime: `lxml`. O pacote público no PyPI é a `0.4.3`.

```bash
pip install calculadora-rtc-regime-regular
```

Para desenvolver a partir do clone:

```bash
cd libs/calculadora-rtc-regime-regular
./install.sh
```

O script cria o `.venv` na raiz (`cenv` se existir, senão `python3 -m venv`), ativa esse ambiente e roda `poetry install --with dev`. Em outro shell: `source .venv/bin/activate`.

O `calculadora-pro.db` vem do Flyway oficial. O gancho deixa o arquivo em `.cache/oficial/java/calculadora/db/calculadora-pro.db`.

```bash
export CALC_DB="$PWD/.cache/oficial/java/calculadora/db/calculadora-pro.db"
```

<a id="consumo"></a>

## Consumo

Importe a fachada. Não abra porta e não monte JSON de controller.

```python
import os

os.environ["CALC_DB"] = "/caminho/calculadora-pro.db"

from calculadora_rtc_regime_regular.consumo import CalculadoraService
from calculadora_rtc_regime_regular.observabilidade import operacao_from_json

payload = {
    "dhFatoGerador": "2026-06-15T12:00:00Z",
    "itens": [{"cClassTrib": "000001", "baseCalculo": "100.00", "quantidade": "1.00"}],
}

operacao = operacao_from_json(payload)  # o mesmo objeto que o serviço Java recebe
roc = CalculadoraService().calcularTributos(operacao)
```

`payload` usa os nomes do JSON que o serviço Java já aceita (`dhFatoGerador`, itens, classificação). `operacao_from_json` só traduz esse documento para `OperacaoCalculadoraInput`.

Fachada em `consumo.py`:

| Classe | Método de entrada |
| --- | --- |
| `CalculadoraService` | `calcularTributos` |
| `ObservabilidadeService` | `processarOperacao` |
| `DadosAbertosService` | `consultarUfs`, `consultarMunicipiosPorSiglaUf`, situações, classificações, NCM, NBS, fundamentação, tipos de DFe |
| `PedagioService` | cálculo de pedágio do regime regular |
| `NfseService` | base, local da operação e indicador da NFS-e |
| `ComponentesBaseCalculoInput` | `setVProd`, `setVFrete` e os demais componentes, `getValor` |

Consulta que lê o banco, como `DadosAbertosService`, precisa de `CALC_DB`. Sem o arquivo, a chamada falha ao abrir o SQLite. O cálculo não cria alíquota: quem chama informa base, alíquota e tratamento, e recebe o mesmo número do Java naquele pin.

<a id="licenca"></a>

## Licença

O código Java oficial não é copiado para este git. A licença dele vale para a obra da Receita e fica reproduzida aqui para o aviso de copyright.

| Obra | Licença | Arquivo |
| --- | --- | --- |
| Esta implementação em Python | MIT, Copyright (c) 2026 Garuso Cruz | [LICENSE](LICENSE) |
| Calculadora Java da Receita Federal, commit `f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4` | MIT, Copyright (c) 2026 Receita Federal do Brasil | [LICENSE-RECEITA.md](LICENSE-RECEITA.md) |

O texto MIT da Receita exige que o aviso de copyright e a permissão acompanhem cópias substanciais daquela obra. Esta implementação conserva esse aviso. A licença desta lib continua sendo a MIT de Garuso Cruz. A MIT da Receita não transfere a titularidade do código dela.
