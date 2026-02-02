using Carter;
using RAgentBackend.Shared.AI;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddHttpClient<IAIClient, OllamaClient>();

builder.Services.AddCarter();

var app = builder.Build();


app.UseHttpsRedirection();


app.MapCarter();

app.Run();