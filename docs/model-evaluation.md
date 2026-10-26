# Local model evaluation

The local Random Forest reached **95.41% accuracy**, **92.87% macro F1**, **94.37% macro precision**, and **91.97% macro recall** on a stratified 20% holdout of 11,704 incidents. The fit used 46,816 incidents, 32 groups, and 19 structured GTD features.

The paper reports 96.82% accuracy for Random Forest on its ≥500-attacks setting. These figures are not directly comparable: this local run uses the supplied 1970–2017 release, a smaller feature set, and does not use the article's DistilBERT summary embeddings or SMOTE-T. Results describe a retrospective research classification task and should not be used for operational attribution or decisions.
