# Augmenter Recipes CommandLine Use 

Transformations and constraints can be used for simple NLP data augmentations. 

The [`examples/`](https://github.com/QData/TextAttack/tree/master/examples) folder includes scripts showing common TextAttack usage for training models, running attacks, and augmenting a CSV file. 

The [documentation website](https://textattack.readthedocs.io/en/latest) contains walkthroughs explaining basic usage of TextAttack, including building a custom transformation and a custom constraint..


## Augmenting Text: `textattack augment`

Many of the components of TextAttack are useful for data augmentation. The `textattack.Augmenter` class
uses a transformation and a list of constraints to augment data. We also offer five built-in recipes
for data augmentation:
- `textattack.WordNetAugmenter` augments text by replacing words with WordNet synonyms
- `textattack.EmbeddingAugmenter` augments text by replacing words with neighbors in the counter-fitted embedding space, with a constraint to ensure their cosine similarity is at least 0.8
- `textattack.CharSwapAugmenter` augments text by substituting, deleting, inserting, and swapping adjacent characters
- `textattack.EasyDataAugmenter` augments text with a combination of word insertions, substitutions and deletions.
- `textattack.CheckListAugmenter` augments text by contraction/extension and by substituting names, locations, numbers.
- `textattack.CLAREAugmenter` augments text by replacing, inserting, and merging with a pre-trained masked language model.

### Augmentation Command-Line Interface
The easiest way to use our data augmentation tools is with `textattack augment <args>`. 

`textattack augment`
takes an input CSV file, the "text" column to augment, along with the number of words to change per augmentation
and the number of augmentations per input example. It outputs a CSV in the same format with all the augmented examples in the proper columns.

> For instance, when given the following as `examples.csv`:

```
"text",label
"the rock is destined to be the 21st century's new conan and that he's going to make a splash even greater than arnold schwarzenegger , jean- claud van damme or steven segal.", 1
"the gorgeously elaborate continuation of 'the lord of the rings' trilogy is so huge that a column of words cannot adequately describe co-writer/director peter jackson's expanded vision of j . r . r . tolkien's middle-earth .", 1
"take care of my cat offers a refreshingly different slice of asian cinema .", 1
"a technically well-made suspenser . . . but its abrupt drop in iq points as it races to the finish line proves simply too discouraging to let slide .", 0
"it's a mystery how the movie could be released in this condition .", 0
```

The command `textattack augment --csv examples.csv --input-column text --recipe embedding --pct-words-to-swap .1 --transformations-per-example 2 --exclude-original`
will augment the `text` column by altering 10% of each example's words, generating twice as many augmentations as original inputs, and exclude the original inputs from the
output CSV. (All of this will be saved to `augment.csv` by default.)

> **Tip:** Just as running attacks interactively, you can also pass `--interactive` to augment samples inputted by the user to quickly try out different augmentation recipes!


After augmentation, here are the contents of `augment.csv`:
```
text,label
"the rock is destined to be the 21st century's newest conan and that he's gonna to make a splashing even stronger than arnold schwarzenegger , jean- claud van damme or steven segal.",1
"the rock is destined to be the 21tk century's novel conan and that he's going to make a splat even greater than arnold schwarzenegger , jean- claud van damme or stevens segal.",1
the gorgeously elaborate continuation of 'the lord of the rings' trilogy is so huge that a column of expression significant adequately describe co-writer/director pedro jackson's expanded vision of j . rs . r . tolkien's middle-earth .,1
the gorgeously elaborate continuation of 'the lordy of the piercings' trilogy is so huge that a column of mots cannot adequately describe co-novelist/director peter jackson's expanded vision of j . r . r . tolkien's middle-earth .,1
take care of my cat offerings a pleasantly several slice of asia cinema .,1
taking care of my cat offers a pleasantly different slice of asiatic kino .,1
a technically good-made suspenser . . . but its abrupt drop in iq points as it races to the finish bloodline proves straightforward too disheartening to let slide .,0
a technically well-made suspenser . . . but its abrupt drop in iq dot as it races to the finish line demonstrates simply too disheartening to leave slide .,0
it's a enigma how the film wo be releases in this condition .,0
it's a enigma how the filmmaking wo be publicized in this condition .,0
```

The 'embedding' augmentation recipe uses counterfitted embedding nearest-neighbors to augment data.

### Augmentation Python API Interface
In addition to the command-line interface, you can augment text dynamically by importing the
`Augmenter` in your own code. All `Augmenter` objects implement `augment` and `augment_many` to generate augmentations
of a string or a list of strings. Here's an example of how to use the `EmbeddingAugmenter` in a python script:

```python
>>> from textattack.augmentation import EmbeddingAugmenter
>>> augmenter = EmbeddingAugmenter()
>>> s = 'What I cannot create, I do not understand.'
>>> augmenter.augment(s)
['What I notable create, I do not understand.', 'What I significant create, I do not understand.', 'What I cannot engender, I do not understand.', 'What I cannot creating, I do not understand.', 'What I cannot creations, I do not understand.', 'What I cannot create, I do not comprehend.', 'What I cannot create, I do not fathom.', 'What I cannot create, I do not understanding.', 'What I cannot create, I do not understands.', 'What I cannot create, I do not understood.', 'What I cannot create, I do not realise.']
```
You can also create your own augmenter from scratch by importing transformations/constraints from `textattack.transformations` and `textattack.constraints`. Here's an example that generates augmentations of a string using `WordSwapRandomCharacterDeletion`:

```python
>>> from textattack.transformations import WordSwapRandomCharacterDeletion
>>> from textattack.transformations import CompositeTransformation
>>> from textattack.augmentation import Augmenter
>>> transformation = CompositeTransformation([WordSwapRandomCharacterDeletion()])
>>> augmenter = Augmenter(transformation=transformation, transformations_per_example=5)
>>> s = 'What I cannot create, I do not understand.'
>>> augmenter.augment(s)
['What I cannot creae, I do not understand.', 'What I cannot creat, I do not understand.', 'What I cannot create, I do not nderstand.', 'What I cannot create, I do nt understand.', 'Wht I cannot create, I do not understand.']
```