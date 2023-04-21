# youtube-conversations
Analyzing conversations from YouTube comments.

This project uses data YouTube comments collected by Wu and Resnick in their [paper](https://github.com/avalanchesiqi/youtube-crosstalk) on YouTube partisan cross-talk

## Project Overview

What is the structure of cross-partisan conversations on YouTube? 
We analyze over 134M comments on 274K YouTube videos to understand this.

![YouTube comments](./figures/yt_comments.png)

We first generate "trees" of conversations by using @-replies as relations between parent and child-nodes.
We find that most conversation trees are under 300 nodes in size, 100 in depth, and 200 in width.

![Tree structure](./figures/structure_tree.png)

Next, we identify unique "chains" of conversations- back-and-forth replies between the same two users within the same tree).
We also find that most chains are made up of at least 40% "visitors", or commentors from the political ideology opposite that of the video being watched.

![Chain structure](./figures/structure_chain.png)

Finally, we develop and define the "comment spread ratio" as a measure of how "spread out" one's comments are across different conversation chains.
A high ratio represents high spread of comments.
A low ratio represents low spread, and therefore deep engagement.

![Comment Spread Overview](./figures/comment_spread_overview.png)


Here we find that commenters are more engaging on their own party's videos than on other parties.

![Comment Spread Results](./figures/comment_spread_results.png)


## Included Files
* ./sources/example_tree_2.json - an example conversation tree
* ./sources/tree_generation.py - build the tree structure from starting dataset (not included; please reach out for details)
* ./sources/chain_generation.py - get unique conversation chains from the conversation tree
* ./7-10_analysis/engagement.py - compile basic statistics of chains and trees
* ./7-19_analysis/visit.ipynb - comment spread ratio of different users
