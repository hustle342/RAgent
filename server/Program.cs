using Carter;
using RAgentBackend.Shared.AI;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddPolicy("MobileAppPolicy", policy =>
    {
        policy.AllowAnyOrigin()   
              .AllowAnyMethod()  
              .AllowAnyHeader();  
    });
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddHttpClient<IAIClient, OllamaClient>();
builder.Services.AddCarter();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseCors("MobileAppPolicy");

app.MapCarter();
app.Run();