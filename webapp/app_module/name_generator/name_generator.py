import random
import pkg_resources, os

resource_package = __name__  ## Could be any module/package name.
resource_path = os.path.join('words.txt')
WORDS = pkg_resources.resource_stream(resource_package, resource_path).read().splitlines()


# WORDS = open(word_file).read().splitlines()

def word_gen():
	word1 = random.choice(WORDS).lower() + '-' + random.choice(WORDS).lower()
	return word1

