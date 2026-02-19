# Aplicacao Cloud-Native de Aluguel de Carros

## Sobre o Projeto

Este projeto implementa uma aplicacao completa de aluguel de carros utilizando arquitetura Cloud-Native no Microsoft Azure. A solucao utiliza Azure Functions para processamento serverless de aluguel e pagamento, alem de uma API BFF (Backend for Frontend) para orquestracao dos servicos.

## Arquitetura da Solucao

```
[Cliente Web/Mobile]
        |
  [API BFF - Aluguel de Carros]
        |
   +----+----+
   |         |
[fnRentProcess]  [fnPayment]
   |              |
[Azure Storage] [Payment Gateway]
```

### Componentes

1. **API BFF (Backend for Frontend)** - API REST que serve como camada de orquestracao entre o front-end e os microsservicos
2. **Azure Function RentProcess** - Funcao serverless responsavel pelo processamento de solicitacoes de aluguel de veiculos
3. **Azure Function Payment** - Funcao serverless responsavel pelo processamento de pagamentos das reservas
4. **Azure Storage** - Armazenamento de dados de veiculos, reservas e transacoes

## Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| Azure Functions | Processamento serverless (RentProcess e Payment) |
| C# / .NET 8 | Linguagem das Azure Functions e API BFF |
| Azure App Service | Hospedagem da API BFF |
| Azure Storage | Persistencia de dados |
| Azure API Management | Gateway e gerenciamento de APIs |
| DrawIO | Desenho da arquitetura |

## Funcionalidades

- Cadastro e listagem de veiculos disponiveis
- Processo de reserva/aluguel de veiculos com validacao de disponibilidade
- Processamento de pagamentos com confirmacao automatica
- Calculo automatico de valores baseado em periodo e tipo de veiculo
- Notificacoes de status de reserva
- API RESTful com documentacao Swagger

## Fluxo de Aluguel

1. Cliente seleciona veiculo e periodo desejado
2. API BFF valida disponibilidade e calcula valor
3. **fnRentProcess** cria a reserva e bloqueia o veiculo
4. **fnPayment** processa o pagamento
5. Confirmacao enviada ao cliente

## Estrutura do Projeto

```
azure-cloud-native-car-rental/
|-- api-bff/                    # API Backend for Frontend
|   |-- Controllers/
|   |-- Models/
|   |-- Services/
|   |-- Program.cs
|-- fnRentProcess/              # Azure Function - Processamento de Aluguel
|   |-- RentProcess.cs
|   |-- host.json
|-- fnPayment/                  # Azure Function - Processamento de Pagamento
|   |-- Payment.cs
|   |-- host.json
|-- docs/
|   |-- architecture.drawio     # Diagrama de arquitetura
|-- README.md
```

## Deploy no Azure

```bash
# Login no Azure
az login

# Criar resource group
az group create --name rg-car-rental --location brazilsouth

# Criar storage account
az storage account create --name stcarrental --resource-group rg-car-rental --location brazilsouth --sku Standard_LRS

# Criar Function App para RentProcess
az functionapp create --name fn-rent-process --resource-group rg-car-rental --storage-account stcarrental --consumption-plan-location brazilsouth --runtime dotnet-isolated --functions-version 4

# Criar Function App para Payment
az functionapp create --name fn-payment --resource-group rg-car-rental --storage-account stcarrental --consumption-plan-location brazilsouth --runtime dotnet-isolated --functions-version 4

# Criar App Service para API BFF
az webapp create --name app-car-rental-bff --resource-group rg-car-rental --plan asp-car-rental --runtime "DOTNET|8.0"
```

## Insights e Aprendizados

- **Arquitetura Cloud-Native**: Separacao de responsabilidades entre BFF, Functions e Storage permite escalabilidade independente
- **Azure Functions**: Plano de consumo ideal para workloads variaveis - paga apenas pelo uso real
- **BFF Pattern**: Backend for Frontend simplifica a logica do cliente e permite otimizacoes especificas por plataforma
- **Serverless + Microservicos**: Combinacao poderosa para aplicacoes cloud-native com baixo custo operacional
- **Event-Driven**: Azure Functions permitem processamento baseado em eventos, ideal para workflows assincronos
- **Managed Identity**: Comunicacao segura entre servicos sem gerenciamento de credenciais

## Referencia

- [Repositorio Original DIO](https://github.com/digitalinnovationone/Microsoft_Application_Platform)
- [Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- [BFF Pattern](https://learn.microsoft.com/azure/architecture/patterns/backends-for-frontends)

## Autor

Desenvolvido como parte do bootcamp **Microsoft Azure Cloud Native** na [DIO](https://www.dio.me/).
