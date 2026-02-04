FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /app

COPY RAgentBackend.csproj .
RUN dotnet restore

COPY . .

RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app

COPY --from=build /app/publish .

ENV ASPNETCORE_HTTP_PORTS=8080
ENTRYPOINT ["dotnet", "RAgentBackend.dll"]