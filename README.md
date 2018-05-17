# Lexical Chains

We create a lexical chains based on the lexical relationships of synonymy, antonymy, and one level of hyper/hyponymy. First of all, we have
to go through the text taking only the words that are in Noun's position. For this we take all the tags that wordnet gives us: NN (Noun, 
singular or mass), NNS (Noun, plural), NNP (Proper noun, singular), NNPS (Proper noun, plural). Once we have all the names we create lists
of relationships.

To perform the lexical chain we have to compare three things for each word:
    - All the nouns we have already in the chain. If there is a noun in the chain, we add one more to the final count.
    - If in the relations list of this noun, we and one word in the actual chain. We append our noun in the same chain. Moreover, we compute a similarity for the two
    words. We have a threshold for determine if the two words can be in the same chain or not.
    - If the nouns that we have already defined in each chain, we look in their relations and if the current noun is in that relation list we will append the noun to the same
    chain. Like in the other case, we compute a similarity between the two words. 
    
In case that none of these relationships are not met we will put a new chain to our final vector. We prune our lexical chain. Since we want only the most important
chains, we delete from the list the chains that only have one element and that word is only repeated once.

# Summary algorithm
We use the lexical chains to automatically create a summary of the input article. The target of the automatic text summarizing is to reduce
a textual document to a summary that retains the important points of the original document. The algorithm that we are going to see tries 
to extract one or more sentences that cover the main topics of the original document using the idea that, if a sentences contains the most
recurrent words in the text, it probably covers most of the topics of the text.
