###########
### AI Controller with HTTP abstracted away
###
### DB is a wrapper for whatever storage is backing the AI
### Use this for storage across games
###
### game contains a "storage" object which is a dict which will be
### persisted after returning
###
###########

from game import RESOURCES, GENERATOR_COST, GENERATOR_IMPROVEMENT_COST, PR_COST, MAX_RESOURCE_GENERATORS, MAX_IMPROVED_RESOURCE_GENERATORS

def start_game(db, game):
	# A new game is starting
	print "Starting a game"

def start_turn(db, game, actions):
	# Start of a turn
	# We have to end the turn with game.end_turn() when we're done
	# alhough we only get 15 seconds to act before our turn is ended by force
	
	# actions is a dict of things which have happened since my last turn,
	# where the keys are player ids, and the values are lists of actions taken,
	# each action is a dict which has an 'action' key (which can be 'purchase-pr', 'trade', etc.)

	def trade_for(requirements):
		# This just figures out how much I can give away without harming the minimum requirements
		# then offers everything extra I have for everything I need.
		# It's very dumb, you should replace it
		request = {}
		offer = {}

		# Loop through each resource ( idea/feature/coffee/website/cash)
		for resource in RESOURCES:
			# If the resource is required for what we're trying to purchase, and the requirements
			# for that purchase are less than we currently have
			if resource in requirements and requirements[resource] > game.resources[resource]:
				# Build a request dictionary which maps the type of resource we want (e.g idea)
				# to the amount of resources we require beyond what we currently have
				request[resource] = requirements[resource] - game.resources[resource]
			else:
				# We don't require this resource. If we have more of this resource than
				# we need for what we're trying to build, offer it in the trade.
				to_offer = game.resources[resource] - requirements.get(resource, 0)
				if to_offer > 0:
					# Offer is a dictionary which maps the type of resource we're offering (e.g. idea)
					# to the amount of resources we are willing to give away
					offer[resource] = to_offer
		# Try to make the trade - it will be offered to all other players, returning False if rejected by all, or returning
		# the accepting player's unique game-specific ID if the trade is accepted.
		return game.trade(offer, request)

	### First try to trade for resources I need

	# If we have less than the maximum number of generators
	if sum(game.generators.values()) < MAX_RESOURCE_GENERATORS:
		# Try to trade for them
		if trade_for(GENERATOR_COST):
			# The trade was successful, although we don't do anything special in this case
			pass

	# If we have less than the maximum number of improved generators
	if sum(game.improved_generators.values()) < MAX_IMPROVED_RESOURCE_GENERATORS:
		# Can improve one of our existing ones
		if trade_for(GENERATOR_IMPROVEMENT_COST):
			# The trade was successful, although we don't do anything special in this case
			pass

	# Always attempt to trade for the resources to purchase PR
	trade_for(PR_COST)

	# Then spend the resources

	# While I have enough resources for a generator, and have less than the maximum number of generators,
	# and it is still my turn (in case of running out of time)
	while game.can_purchase_generator() and game.turn:
		# Purchase a generator, this will return the type of generator purchased
		generator_type = game.purchase_generator()
		print "Purchased %s" % generator_type

	# While I have enough resources to upgrade a generator, and have less than the maximum number of generators,
	# and it is still my turn (in case of running out of time)
	while game.can_upgrade_generator() and game.turn:
		# Upgrade a generator, this will return the type of generator upgraded
		# (I could also pass the type of generator to upgrade as a parameter to upgrade a
		#  specific one)
		generator_type = game.upgrade_generator()
		print "Upgraded %s" % generator_type

	# While I have enough resources to purchase PR and it is still my turn (in case of running out of time)
	while game.can_purchase_pr() and game.turn:
		# Purchase PR
		game.purchase_pr()
		print "Purchased PR"

	if game.turn:
		game.end_turn()

def time_up(db, game):
	# We have ran out of time for this turn, it has been forced to end
	pass

def end_game(db, game, error=None):
	if error:
		print "Something went wrong! %s" % error
	else:
		print "Game over"

def incoming_trade(db, game, player, offering, requesting):
	# "player" is the unique game-specific ID of the player offering the trade
	# offering is a dictionary mapping resource types (e.g. idea) to the number of resources of that type being offered
	# requesting is a dictionary mapping resource types (e.g. idea) to the number of resources of that type being requested
	# As long as I'm gaining at least one resource more than I'm giving away, I'll accept
	if sum(offering.values()) > sum(requesting.values()):
		return True
	# Otherwise reject, regardless of what is being offered or requested
	return False