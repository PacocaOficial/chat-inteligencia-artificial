import os

from read_file import read_file

REDE_SOCIAL = "Paçoca"
LINK = os.getenv('LINK')
LINK = "https://react.pacoca.net"
ABOUT = f"{LINK}/sobre"
USE_OF_TERMS = f"{LINK}/termos-uso"
GUIDELINES = f"{LINK}/diretrizes"
READ_BOOKS = os.getenv('READ_BOOKS')
DISCORD = os.getenv('DISCORD')

LINKS = {
    "link oficial": LINK,
    "termos de uso": f"{LINK}/termos-uso",
    "diretrizes": f"{LINK}/termos-uso",
    "login": f"{LINK}/login",
    "criar conta": f"{LINK}/cadastro",
    "doação": f"{LINK}/doacao",
    "Paçoca games - jogos online do paçoca": f"{LINK}/jogos",
    "readbooks - read books": READ_BOOKS,
    "configurações": f"{LINK}/configuracoes",
    "configurar privacidade": f"{LINK}/privacidade",
    "visualizar sessões ativas": f"{LINK}/sessoes-ativas",
    "configurar notificações": f"{LINK}/configuracoes/notificacoes",
    "premium - pagar verificado": f"{LINK}/verificado",
    "minhas comunidades": f"{LINK}/comunidades",
    "discord oficial": DISCORD,
    "baixar paçoca": f"{LINK}/download",
    "significado dos selos": f"{LINK}/significado-selos",
    "dashboard com dados atualizados do Paçoca": f"{LINK}/dashboard",
}

DEFAULT_TEXT = (
    f"Você é uma IA para a plataforma/rede social {REDE_SOCIAL} ela é real e possui usuários ativos."
    f"Por padrão, você deve considerar que qualquer assunto sobre Paçoca ou paçoca é sobre a rede social."
    f"Tudo que você precisa saber sobre a rede social e sobre sua criação está em: {read_file("sobre.txt")}."
    f"Tudo que você precisa saber sobre os selos está em: {read_file("significado_selos.txt")}."
    f"Diretrizes da rede social e da comunidade disponível em: {GUIDELINES}."
    f"Termos de uso da rede social e da comunidade disponível em: {USE_OF_TERMS}."
    f"Números reais da pladaforma, como quantidade de usuárois em: {LINK}/dashboard."
   "Todos os links úteis e oficiais:\n" +
    "\n".join([f"{k}: {v}" for k, v in LINKS.items()])
)