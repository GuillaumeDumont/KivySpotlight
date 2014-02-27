###############################################################################
# 	@package docstring
#
#	@author 	Guillaume Dumont
# 	@project	KivySpotlight
#	@repo	 	http://github.com/GuillaumeDumont/KivySpotlight
#
#	@brief		Implementation of the "FuzzySearch" as done in Sublime Text
#
###############################################################################
class weight:
	acronym = 5
	adjacent = 2
	lonely = 1


def tag(search, sentence, bounty = 0, solution = [], score = 0, index = 0):
	if not sentence and search:
		return (0, None)
	if not search:
		return (score + bounty, solution)
	s = search[0]
 	first_letter = True if index == 0 else False
 	new_score = score
	score1 = score2 = 0
	solution1 = solution2 = None 
	for i, c in enumerate(sentence):
		if c == s or c.upper() == s.upper():
			new_bounty = 0
			if c == c.upper() or first_letter: # acronym
				new_bounty = weight.acronym * (weight.adjacent if bounty else weight.lonely)
			else:
				new_bounty = weight.adjacent * (bounty if bounty > weight.lonely else weight.adjacent) if bounty else weight.lonely
			new_solution = list(solution)
			new_solution.append(index + i)
			score1, solution1 = tag(search[1:], sentence[i+1:], new_bounty, new_solution, new_score, index + i + 1)
			score2, solution2 = tag(search, sentence[i+1:], 0, solution, new_score, index + i + 1)
			return (score1, solution1) if score1 >= score2 else (score2, solution2)
		first_letter = True if c == ' ' else False
		new_score += bounty
		bounty = 0
	return (score + bounty, solution) if not search else (0, None)

'''
search = 'togglE'

sentence = 'Select Toggle'
score, solution = tag(search, sentence)
print score
if solution:
	print map((lambda i : sentence[i]) ,solution)

'''