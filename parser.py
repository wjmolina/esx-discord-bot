from re import search

from model import Author, Bet, Vote


async def execute(client, message):
    command, args = search(MESSAGE_REGEX, message.content).groups()
    return await COMMANDS[command][0](client, message, args)


async def create_bet(client, message, args):
    bet = Bet.create(Author.create_or_read_by_discord_id(message.author.id).id, args)
    return f"You successfully created a bet with ID `{bet.id}` and value `{args}`."


async def create_vote(client, message, args):
    bet_id, *value = args.split(" ")
    bet_id, value = int(bet_id), " ".join(value)
    author_id = Author.create_or_read_by_discord_id(message.author.id).id
    Vote.create(bet_id, author_id, value)
    return f"You successfully created a vote with value `{value}`."


async def read_bets(client, message, args):
    result = ""
    for bet in Bet.read():
        result += f"**ID**: `{bet.id}`\n"
        result += f"**Value**: `{bet.value}`\n"
        result += (
            f"**Author**: `{bet.author_id}` "
            f"({(await client.fetch_user(bet.author.discord_id)).name})\n"
        )
        result += f"**Votes**: {len(bet.votes)}\n"
        if bet.winner_id:
            result += (
                f"**Winner**: `{bet.winner.id}` "
                f"({(await client.fetch_user(bet.winner.discord_id)).name})\n"
            )
        result += "\n"
    return result or "There are no bets."


async def read_votes(client, message, args):
    id = int(args)
    result = ""
    for vote in Bet.read(id).votes:
        result += f"**Value**: `{vote.value}`\n"
        result += (
            f"**Author**: `{vote.author_id}` "
            f"({(await client.fetch_user(vote.author.discord_id)).name})\n"
        )
        result += "\n"
    return result or "There are no votes."


async def read_commands(client, message, args):
    result = ""
    for command, (_, args) in COMMANDS.items():
        result += f"`{command}` {args}\n"
    return result or "There are no commands."


async def update_winner(client, message, args):
    bet_id, winner_id = args.split(" ")
    bet_id, winner_id = (
        int(bet_id),
        int(winner_id) if winner_id.lower() != "none" else None,
    )
    bet = Bet.read(bet_id)
    bet.update_winner(winner_id)
    winner_string = (
        f"author with ID `{winner_id}` ({(await client.fetch_user(bet.winner.discord_id)).name})"
        if winner_id
        else "reset"
    )
    return f"The winner of bet with ID `{bet_id}` is {winner_string}."


async def read_info(client, message, args):
    return "Do you have conflicting predictions? Bet on them. I will keep score."


TAG = "!esxbet"
MESSAGE_REGEX = f"{TAG} (\w+)(?: (.+))?"
COMMANDS = {
    "create_bet": (create_bet, "`<value>`"),
    "read_bets": (read_bets, ""),
    "create_vote": (create_vote, "`<bet_id>` `<value>`"),
    "read_votes": (read_votes, "`<bet_id>`"),
    "read_commands": (read_commands, ""),
    "update_winner": (update_winner, "`<bet_id>` `<author_id>`"),
    "read_info": (read_info, ""),
}
