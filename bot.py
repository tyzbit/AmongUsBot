#!/usr/bin/env python3
import discord
import json
import logging
import os
import pathlib
import random
import string
import sys

class GameState:
  def __init__(self):
    self.load_state_and_config()

  def load_state_and_config(self):
    """
    Initializes the game state by reading it from a file
    """
    self.current_dir = str(pathlib.Path(__file__).resolve().parent)
    self.state={
      "active_games": {},
      "historical_game_summaries": {}
    }
    config_file = f'{current_dir}/config.json'
    try:
      with open(config_file, 'r') as read_file:
        try:
          self.config = json.load(read_file)
        except Exception as e:
          logger.error(f'Unable to read config file at {config_file}, {e}')
          sys.exit(1)
    except Exception as e:
      logger.warning(f'Config file not found at {config_file}, exiting')
      sys.exit(1)
    
    state_file = f'{current_dir}/state.json'
    try:
      with open(state_file, 'r') as read_file:
        try:
          self.state = json.load(read_file)
        except Exception as e:
          logger.error(f'Unable to read state file at {state_file}, {e}')
          sys.exit(1)
    except Exception as e:
      logger.warning(f'State file not found at {state_file}, creating new state')
      self.save_game_state()

    return 'Successfully loaded game state and config'

  def get_game_state(self):
    return self.state
  
  def clear_game_state(self):
    logger.info('Clearing state')
    self.state = {}
    self.save_game_state()
    return 'State cleared!'

  def save_game_state(self):
    logger.info('Saving state')
    try:
      f = open(self.current_dir + '/state.json', 'w')
    except Exception:
      logger.warning('Unable to open state file, trying to create it...')
      pathlib.Path(self.current_dir + '/state.json').touch(exist_ok=True)
      try:
        f = open(self.current_dir + '/state.json', 'w')
      except Exception as e:
        logger.error('Still unable to open state file after creating it, exiting...')
        sys.exit(1)

    try:
      f.write(json.dumps(self.state))
      f.close()
    except Exception:
      logger.error(f'Unable to write state file, exiting...')
      sys.exit(1)
    return 'Successfully saved game state!'

  def get_summary(self):
    active_games = len(self.state['active_games'])
    historical_game_summaries = len(self.state['historical_game_summaries'])
    players = 0
    for active_game in self.state['active_games']:
      if 'players' in active_game:
        for players in active_game['players']:
          players += 1
    return f'{active_games} games being played by {players} players.  {total_games} total games played.'
  
  def add_new_game(self, game_code, embed):
    self.active_games += { game_code: embed }
  
  def get_existing_active_game(self, game_code, embed):
    if game_code not in self.active_games:
      logger.debug(f'Game code {game_code} not found in active games!')
    else:
      return self.active_games[game_code]
  
  def get_all_game_codes(self):
    active_games = self.active_games.keys()
    historical_games = self.historical_games.keys()
    all_games = active_games + historical_games
    return all_games

async def start_new_game(game_state, message):
  valid_characters = string.ascii_uppercase
  game_code_length = 6
  if 'gameCodeLength' in config:
    game_code_length = config['gameCodeLength']
  game_code_found = False
  tries = 0
  while game_code_found = False:
    proposed_game_code = ''.join(random.choice(letters) for i in range(game_code_length))
    tries += 1
    if proposed_game_code not in game_state.get_all_game_codes():
      game_code = proposed_game_code
      game_code_found = True
    if tries = 10:
      logger.debug('Tried to generate a new code 10 times and failed')
      return False
  logger.debug(f'Starting new AU game ID {game_code}')
  embedVar = discord.Embed(title="", description="Desc", color=0x00ff00)
  #embedVar.add_field(name="Field1", value="hi", inline=False)
  returned_embed = await send_embed(message.author, embedVar)
  game_state.add_new_game(game_code, returned_embed)

async def update_current_game(game_state, embed):
  logger.debug('Updating current game')
  embedVar = discord.Embed(title="Among us New", description="Desc", color=0x00ff00)
  embedVar.add_field(name="Field1", value="hi", inline=False)
  current_embed = game_state.get_existing_active_game(embed)
  await current_embed.edit(embed=embedVar)

async def get_summary(game_state, message):
  logger.debug('Sending summary')
  summary = game_state.get_summary()
  return await message.channel.send(summary)

async def manually_save_state(game_state, message):
  logger.debug('Manually saving state')
  status = game_state.save_game_state()
  return await message.channel.send(status)

async def clear_game_state(game_state, message):
  logger.debug('Manually clearing game state')
  status = game_state.clear_game_state()
  return await message.channel.send(status)

async def load_state_and_config(game_state, message):
  logger.debug('Manually reloading game state')
  status = game_state.load_state_and_config()
  return await message.channel.send(status)

async def send_dm(user, message):
  logger.debug('Sending a message')
  return await user.send(message)

async def send_embed(user, embed):
  logger.debug('Sending a message')
  return await user.send(embed=embed)

def main(game_state):
  logger.info('Starting bot...')

  discordToken = game_state.config['discordToken']
  client = discord.Client()

  possible_commands={
    "!au": "start_new_game",
    "!aujoin": "join_active_game",
    "!auedit": "update_current_game",
    "!ausummary": "get_summary",
    "!ausave": "manually_save_state",
    "!aureload": "load_state_and_config"
  }
  @client.event
  async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')
  
  @client.event
  async def on_message(message):
    if message.author == client.user:
      return

    for command in possible_commands:
      if message.content.startswith(command):
        function = possible_commands[message.content.split(' ')[0]]
        call_function = globals()[function]
        await call_function(game_state, message)

  client.run(discordToken)

if __name__ == '__main__':
  current_dir = pathlib.Path(__file__).resolve().parent

  # Set up logging to console and file
  logger = logging.getLogger('bot')
  fh = logging.FileHandler(str(current_dir) + '/bot.log')
  ch = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
  logger.addHandler(fh)
  logger.addHandler(ch)

  # Init state
  game_state = GameState()
  config = game_state.config

  # Set loglevel
  level_config = {
    'debug': logging.DEBUG,
    'info': logging.INFO, 
    'warn': logging.WARNING,
    'error': logging.ERROR
  }
  if 'logLevel' in config:
    loglevel = config['logLevel']
    logger.setLevel(level_config[loglevel])
    logger.info(f'Logging set to {config["logLevel"]}...')
  else:
    logger.setLevel(logging.WARN)
    logger.warn(f'Logging set to warn...')

  if 'discordToken' not in config:
    logger.error('\'discordToken\' is not set in config')
    sys.exit(1)
  discordToken = config['discordToken']
  main(game_state)