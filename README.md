# calculadora-rtc-regime-regular

[![versão 0.1.0](https://img.shields.io/badge/vers%C3%A3o-0.1.0-blue)](https://github.com/garusocruz/calculadora-rtc-regime-regular)
[![pin oficial f1eebd7](https://img.shields.io/badge/pin%20oficial-f1eebd7-orange)](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/commit/f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4)
[![Cloud Build equivalência](https://img.shields.io/badge/Cloud%20Build-equival%C3%AAncia-1a73e8?logo=googlecloud&logoColor=white)](cloudbuild.yaml)
[![licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)](LICENSE)
[![Java oficial MIT](https://img.shields.io/badge/Java%20oficial-MIT%20Receita%20Federal-blue)](LICENSE-RECEITA.md)

Releitura em Python da calculadora oficial em Java da Receita Federal. Não é um fork: o código Java não entra neste repositório. O cálculo segue o commit pinado abaixo.

| | |
| --- | --- |
| Fonte oficial | [ReceitaFederal/calculadora-rtc-regime-regular](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular) |
| Commit pinado | [`f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4`](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/commit/f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4) |
| Licença do Java | MIT, Copyright (c) 2026 Receita Federal do Brasil — [LICENSE-RECEITA.md](LICENSE-RECEITA.md) |
| Licença desta lib | MIT, Copyright (c) 2026 Garuso Cruz — [LICENSE](LICENSE) |

Esta biblioteca não emite nota, não assina XML e não chama a Sefin.

## Índice

- [Arquitetura](#arquitetura)
- [Equivalência](#equivalencia)
- [Última validação](#ultima-validacao)
- [Atualização do pin](#atualizacao-do-pin)
- [Instalação](#instalacao)
- [Consumo](#consumo)
- [Licença](#licenca)

A lib não sobe API. O controller, o MockMvc e o HTTP 400 ficam no Java. Quem consome chama o serviço, com o mesmo nome de método da classe Java, em `calculadora_rtc_regime_regular.consumo`.

O DANFSe não faz parte deste repositório nem do Java do regime regular. O PDF da NFS-e é o módulo Go `danfse-service`, em https://github.com/ReceitaFederal/calculadora-rtc-gerador-danfse, pin `8d79e6b2f7fad6375340afcb51c85ed370c64a14`.

<a id="arquitetura"></a>

## Arquitetura

```mermaid
flowchart TB
  subgraph oficial ["Receita Federal — pin f1eebd7"]
    javaSrc["Serviços Java"]
    flyway["Flyway oficial"]
    surefire["JUnit no surefire"]
    javaSrc --> surefire
    flyway --> db["calculadora-pro.db somente leitura"]
    db --> surefire
  end

  subgraph lib ["Esta lib Python"]
    fachada["consumo.py — nome Java"]
    servico["serviços em snake_case"]
    politica["arredondamento.py — única política numérica"]
    fachada --> servico
    servico --> politica
    servico --> dbPy["mesmo calculadora-pro.db"]
  end

  db --> dbPy
  surefire --> gate["scripts/equivalencia.sh"]
  pytest["pytest com o nome classe.método"] --> gate
  dbPy --> pytest

  danfse["DANFSe em Go — fora desta lib"]
```

O banco não é gerado pela lib. O script de equivalência baixa o pin, roda o Flyway oficial e grava `calculadora-pro.db`. A lib abre esse arquivo em modo somente leitura. O caminho entra por `CALC_DB`. Sem a variável, ela procura `calculadora/db/calculadora-pro.db` a partir do diretório corrente.

<a id="equivalencia"></a>

## Equivalência

O gancho `scripts/hooks/pre-push.sh` chama `scripts/equivalencia.sh`. O Cloud Build dispara o mesmo script pelo arquivo `cloudbuild.yaml`. Os triggers, no plano de delivery da fundação, são `calculadora-rtc-regime-regular-pr` (pull request para `main`) e `calculadora-rtc-regime-regular-main` (push em `main`). Não há workflow do GitHub Actions. O build não publica pacote.

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

Data: 22 de novembro de 2026. O repositório é https://github.com/garusocruz/calculadora-rtc-regime-regular. O check remoto ainda é o script local. O Cloud Build grava o status quando o plano de delivery da fundação estiver aplicado.

O `scripts/hooks/pre-push.sh` completo, log em `.cache/pre-push.log`, terminou `pre-push OK`.

| Checagem | Saída |
| --- | --- |
| Maven test | a suíte Java do pin passou |
| Pytest | 1758 passaram, 6 ignorados, 32,80 s |
| Cobertura | 93,82% de 6506 sentenças. O mínimo é 80% |
| Java no corte daquele momento | 672 unitários, 344 e2e |
| Python no relatório | 3079 chaves |
| Sem par | 0 |
| Resultado diferente | 0 |
| Frase final | `Equivalência: a mesma suíte passou nas duas.` |

Depois desse log, os testes de arquitetura passaram a contar no corte. A comparação seguinte usou o surefire já gerado e um pytest novo, sem repetir o Maven: 1020 casos Java, 0 sem par, 0 com resultado diferente.

<a id="atualizacao-do-pin"></a>

## Atualização do pin

A Receita não aceita pull request externo. O acompanhamento é a inscrição no repositório oficial, em Watch, com Issues, Releases e Security alerts. Pull requests e Discussions ficam desligados.

Os três pins oficiais estão em `lynko-workspace/initiatives/faturae/receita-rtc-pins.json`. O deste repositório também é o padrão `OFICIAL_SHA` de `scripts/equivalencia.sh`.

Quando sai um release, um alerta de segurança ou uma issue que muda regra:

1. Ler o commit novo no repositório oficial.
2. Trocar o pin no `OFICIAL_SHA` e no JSON de pins.
3. Rodar `bash scripts/hooks/pre-push.sh`.
4. Cada nome que faltar é um serviço que o controller Java chama. Portar esse serviço. A fachada em `consumo.py` conserva a classe e o método Java. Por dentro, a função nova fica em snake_case.
5. Repetir o gancho até `pre-push OK`.

Não se recoloca esse cálculo em `backends/faturae`. Não se publica em Artifact Registry nem em Cloud Build da Lynko.

<a id="instalacao"></a>

## Instalação

Python 3.12 ou superior. Dependência de runtime: `lxml`.

```bash
cd libs/calculadora-rtc-regime-regular
poetry install
```

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

Esta lib é uma releitura em Python. O código Java oficial não é copiado para este git. A licença dele vale para a obra da Receita e fica reproduzida aqui para o aviso de copyright.

| Obra | Licença | Arquivo |
| --- | --- | --- |
| Esta releitura em Python | MIT, Copyright (c) 2026 Garuso Cruz | [LICENSE](LICENSE) |
| Calculadora Java da Receita Federal, commit `f1eebd7ce3157423b1a6aaca7dc1d6c3395452c4` | MIT, Copyright (c) 2026 Receita Federal do Brasil | [LICENSE-RECEITA.md](LICENSE-RECEITA.md) |

O texto MIT da Receita exige que o aviso de copyright e a permissão acompanhem cópias substanciais daquela obra. A releitura conserva esse aviso. Não substitui a licença desta lib.
