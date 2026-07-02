import warnings
# Silencia o aviso de falta de acelerador C antes de importar o thefuzz
warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import api
import database
import matcher

console = Console()

def exibir_menu():
    console.print(Panel.fit(
        "[bold blue]🏦 Sistema de Busca Aproximada de Instituições Bancárias[/bold blue]\n"
        "[1] Sincronizar Bancos (API -> SQLite)\n"
        "[2] Busca de Banco por Nome (Aproximação)\n"
        "[3] Busca por Código com Tolerância\n"
        "[4] Agrupar Bancos por Similaridade\n"
        "[5] Corrigir Nome Digitado\n"
        "[0] Sair",
        title="Menu Principal"
    ))

def acao_sincronizar():
    with console.status("[bold green]Buscando dados da BrasilAPI..."):
        dados = api.buscar_bancos_api()
    if dados:
        qtd = database.salvar_bancos(dados)
        console.print(f"[bold green]✓ Sucesso![/bold green] {qtd} bancos sincronizados no banco local.")
    else:
        console.print("[bold red]❌ Falha ao sincronizar dados.[/bold red]")

def acao_busca_nome():
    bancos = database.listar_todos_bancos()
    if not bancos:
        console.print("[yellow]⚠️ O banco de dados está vazio. Sincronize primeiro![/yellow]")
        return
        
    termo = Prompt.ask("Digite o nome ou fragmento do banco")
    resultados = matcher.buscar_por_aproximacao_nome(termo, bancos)
    
    table = Table(title=f"Resultados para: '{termo}'")
    table.add_column("Código", style="cyan")
    table.add_column("Nome Curto", style="magenta")
    table.add_column("Score", justify="right")
    table.add_column("Correspondência", justify="center")

    for b in resultados:
        score = b["score"]
        status_match = "[bold green]EXATA[/bold green]" if score == 100 else "[dim]Parcial[/dim]"
        score_color = f"[green]{score}[/green]" if score >= 80 else f"[yellow]{score}[/yellow]"
        
        table.add_row(
            str(b["code"] or "N/A"),
            b["name"] or "N/A",
            score_color,
            status_match
        )
    console.print(table)

def acao_busca_codigo():
    bancos = database.listar_todos_bancos()
    if not bancos:
        console.print("[yellow]⚠️ Sincronize os dados primeiro![/yellow]")
        return
        
    codigo = Prompt.ask("Digite o código numérico (admite erros de digitação)")
    resultados = matcher.buscar_por_codigo_tolerante(codigo, bancos)
    
    if not resultados:
        console.print("[red]Nenhum código similar foi encontrado.[/red]")
        return

    table = Table(title=f"Códigos similares encontrados para '{codigo}'")
    table.add_column("Código Cadastrado", style="cyan")
    table.add_column("Nome", style="magenta")
    table.add_column("Confiança do Código", justify="right")
    
    for b in resultados:
        table.add_row(str(b["code"]), b["name"], f"{b['score']}%")
    console.print(table)

def acao_agrupar():
    bancos = database.listar_todos_bancos()
    if not bancos:
        console.print("[yellow]⚠️ Sincronize os dados primeiro![/yellow]")
        return
        
    with console.status("[bold green]Analisando similaridades par a par (isso pode levar alguns segundos)..."):
        grupos = matcher.agrupar_bancos_similares(bancos)
        
    if not grupos:
        console.print("[green]Nenhum grupo de alta similaridade redundante foi encontrado.[/green]")
        return
        
    table = Table(title="Grupos de Bancos com Nomes Similares")
    table.add_column("Nome Representativo", style="bold yellow")
    table.add_column("Variações Encontradas (Código - Nome)", style="white")
    
    for nome_rep, membros in grupos.items():
        variacoes = "\n".join([f"• {m['code']} - {m['name']}" for m in membros])
        table.add_row(nome_rep, variacoes)
        
    console.print(table)

def acao_corrigir_nome():
    bancos = database.listar_todos_bancos()
    if not bancos:
        console.print("[yellow]⚠️ Sincronize os dados primeiro![/yellow]")
        return
        
    digitado = Prompt.ask("Digite o nome do banco com possíveis erros")
    top_1 = matcher.buscar_por_aproximacao_nome(digitado, bancos, limite=1)
    
    if top_1:
        sugestao = top_1[0]
        console.print(Panel(
            f"[bold text]Texto digitado:[/bold text] {digitado}\n"
            f"[bold green]Sugestão corrigida:[/bold green] {sugestao['name']} ({sugestao['fullName']})\n"
            f"[bold blue]Nível de Confiança:[/bold blue] {sugestao['score']}%",
            title="Corretor Ortográfico de Termos"
        ))

def main():
    while True:
        exibir_menu()
        opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "4", "5", "0"], default="0")
        
        if opcao == "1":
            acao_sincronizar()
        elif opcao == "2":
            acao_busca_nome()
        elif opcao == "3":
            acao_busca_codigo()
        elif opcao == "4":
            acao_agrupar()
        elif opcao == "5":
            acao_corrigir_nome()
        elif opcao == "0":
            console.print("[bold red]Encerrando aplicação... Até mais![/bold red]")
            break
        console.print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    main()
