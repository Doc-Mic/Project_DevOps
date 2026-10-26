# Model and data choices

## Research source

The selected recent publication is Abdalsalam et al. (2024), “Terrorism group prediction using feature combination and BiGRU with self-attention mechanism,” PeerJ Computer Science 10:e2252, DOI [10.7717/peerj-cs.2252](https://doi.org/10.7717/peerj-cs.2252). Its framework combines structured GTD attributes with DistilBERT features from event summaries and uses SMOTE-T. The article compares ten models, including Random Forest, and reports a 96.82% holdout accuracy for its Random Forest experiment with groups responsible for at least 500 attacks.

## Local adaptation

The supplied GTD file is the 1970–2017 release. In this copy, excluding the `Unknown` target and retaining groups with at least 500 records yields 32 groups and 58,520 incidents. The application trains the article's Random Forest model family on this subset. It uses 19 structured fields: year, month, day, extension, country, region, coordinates, location specificity, vicinity, multiple-incident flag, success, suicide, attack type, target type and subtype, target nationality, weapon type and subtype. The target `gname` is never sent to the model as an input.

Text summaries and post-incident casualty counts are excluded. The local model does not implement the article's DistilBERT embeddings or SMOTE-T, so the reported article score is context only and should not be treated as a target for this run. The training script records the actual held-out metrics in `docs/model-evaluation.md`.

The model uses a stratified random 80/20 holdout with fixed random seed 42. A random holdout measures classification of held-out records drawn from the same historical period; it does not establish performance on future incidents, newly formed organizations, or changing conditions. The saved bundle contains the fitted imputers, one-hot encoder, Random Forest, input feature order, allowed category codes, and model provenance.

## Use and interpretation

Predictions are uncertain retrospective classifications of historical event records. A probability is the model's score across its known training classes, not a calibrated probability that a named organization actually committed an attack. The interface and API display this limitation. This project is for coursework and reproducible model-serving practice only.