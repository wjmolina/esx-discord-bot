from re import search

from google.cloud import translate_v2

from model import Author, Bet, Vote


async def execute(client, message):
    command, args = search(MESSAGE_REGEX, message.content).groups()
    try:
        return await COMMANDS[command][0](client, message, args)
    except Exception as exception:
        return exception


async def create_bet(client, message, args):
    bet = Bet.create(Author.create_or_read_by_discord_id(message.author.id).id, args)
    return f"You successfully created a bet with ID `{bet.id}` and value `{args}`."


async def create_vote(client, message, args):
    bet_id, *value = args.split(" ")
    bet_id, value = int(bet_id), " ".join(value)
    author_id = Author.create_or_read_by_discord_id(message.author.id).id
    Vote.create(bet_id, author_id, value)
    return f"You successfully created a vote with value `{value}`."


async def read_bets_helper(client, *, exclude_open=False, exclude_closed=True):
    result = ""
    for bet in Bet.read(exclude_open=exclude_open, exclude_closed=exclude_closed):
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


async def read_bets(client, message, args):
    return await read_bets_helper(client, exclude_closed=False)


async def read_bets_open(client, message, args):
    return await read_bets_helper(client)


async def read_bets_closed(client, message, args):
    return await read_bets_helper(client, exclude_open=True, exclude_closed=False)


async def read_votes(client, message, args):
    bet_id = int(args)
    result = ""
    for vote in Bet.read(bet_id=bet_id).votes:
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
    bet = Bet.read(bet_id=bet_id)
    bet.update_winner(winner_id)
    winner_string = (
        f"author with ID `{winner_id}` ({(await client.fetch_user(bet.winner.discord_id)).name})"
        if winner_id
        else "reset"
    )
    return f"The winner of bet with ID `{bet_id}` is {winner_string}."


async def read_info(client, message, args):
    return "Do you have conflicting predictions? Bet on them. I will keep score."


async def read_standings(client, message, args):
    authors = sorted(Author.read(), key=lambda author: -len(author.won))
    result = ""
    for author in authors:
        result += f"**ID**: `{author.id}` ({(await client.fetch_user(author.discord_id)).name})\n"
        n_bets = len([vote for vote in author.votes if vote.bet.winner])
        result += (
            f"**Bets Won**: {len(author.won)} out of "
            f"{n_bets} ({(len(author.won) / n_bets * 100):.2f}%)\n"
        )
        result += "\n"
    return result or "There are no authors."


async def translate(client, message, args):
    return translate_v2.Client().translate(message.content, target_language="en")["translatedText"]


TAG = "!owl"
MESSAGE_REGEX = f"{TAG} (\S+)(?: (.+))?"
COMMANDS = {
    "create-bet": (create_bet, "`<value>`"),
    "create-vote": (create_vote, "`<bet_id>` `<value>`"),
    "read-bets": (read_bets, ""),
    "read-bets-open": (read_bets_open, ""),
    "read-bets-closed": (read_bets_closed, ""),
    "read-votes": (read_votes, "`<bet_id>`"),
    "read-commands": (read_commands, ""),
    "read-info": (read_info, ""),
    "read-standings": (read_standings, ""),
    "update-winner": (update_winner, "`<bet_id>` `<author_id>`"),
    "translate": (translate, "`<text>`"),
}
