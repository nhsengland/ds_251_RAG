# DS_251_RAG: Exploring the use of RAG in NHS England
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)
 [![licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT "MIT License")
 

:exclamation: Warning: this repository may contain references internal to NHS England that cannot be accessed publicly

This project aims to explore the potential uses and efficacy of "Retrieval Augmented Generation" (RAG) within NHS England.

This will principally involve:

* [x] **WP1**: Making a simple RAG pipeline -> [here](dev.ipynb)
* [ ] **WP2**: Make reusable current code
* [ ] **WP3**: Methodology exploration - how to take RAG further
* [ ] **WP4**: Evaluation
* [ ] **WP5**: Explainer

## Contact
**This repository is maintained by NHS England Data Science Team**.
> _To contact us raise an issue on Github or via [email](mailto:england.rapchampions@nhs.net)._
> 
> See our (and our colleagues') other work here: [NHS England Analytical Services](https://github.com/NHSDigital/data-analytics-services)

## Description

> Provide more detailed overview of the project, including (if relevant) a description of the publication process.

This repository is intended to function as a template for Python RAP projects at NHS England.

You can learn more about project structure and why it's important in the ['project structure and packaging guide'](https://nhsdigital.github.io/rap-community-of-practice/training_resources/python/project-structure-and-packaging/) of the RAP community of practice Github repo, a central source of RAP knowledge.

_You can edit any part of this document. The licence section **must be edited** before publishing this repository publicly. For more information about publishing your project please see the ['how to publish your code in the open' guide](https://nhsdigital.github.io/rap-community-of-practice/implementing_RAP/how-to-publish-your-code-in-the-open/)._

### WP1: Make a simple RAP pipeline

* We need to make a simple RAP pipeline to use to explore this technique
* It doesn't need to be that complex - but we do need to be able to turn the "RAG" component on or off - so 
we can test what effect it has.

The basic structure is described below:

 ```mermaid
    graph LR

    A[Receive Query] --> L{RAG?}

    L -- Yes --> B[Pass to database]

    L -- No --> J

    B --> H[(Vectorstore)]

    H --> I[Retrieve documents]

    I --> F[Prompt: Inject Metadata] 
    F --> G[Prompt: Stuff Documents]

    G --> J[Submit prompt to LLM]

    J --> K[Get response]

```

The code for the RAG pipeline is found here: [`src/models.py`](./src/models.py)

You can run the RAG pipeline here: [`dev.ipynb`](dev.ipynb)

### WP2: Make current code reusable 

* We want to meet the silver RAP standard, hence the code needs better documentation, testing and breaking up into reusable chunks.

### WP3: Methodology exploration

* Setting out how RAG might be further developed for use in the business, or even just a discussion of more advanced implementations and their benefits (and risks / costs).
* e.g.
    * RAG-fusion: https://github.com/Raudaschl/rag-fusion
    * CRAG: https://www.marktechpost.com/2024/02/03/enhancing-the-accuracy-of-large-language-models-with-corrective-retrieval-augmented-generation-crag/
    * llamaindex: https://www.llamaindex.ai/
    * langchain: https://www.langchain.com/
    * Agents
    * RAGAS: https://docs.ragas.io/en/stable/

### WP4: Evaluation

* we need to understand how good these tools are at answering questions /summarising documents
* A relatively simple approach we can start with is, to use the NHS Conditions website (https://www.nhs.uk/conditions/), and see if it can answer questions correctly about that content, and if turning RAG on and off makes any difference.
    * Fortunately cogstack have made an AI which produces question/answer pairs for NHS conditions- https://github.com/CogStack/opengpt
* We could then measure the similarity of the "correct" answer with the generated answer using "LLM-as-a-judge" - then compare the scores for RAG and non-RAG
* There a number of benchmarks, such as [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/), however it is not clear that good performance on these will mean it will perform well on tasks relevant to our business.
* More discussion about evaluating RAG can be found in these papers: 
    * Zhou et al. 2023: https://arxiv.org/abs/2311.05112


### WP5: Explainer

* Senior decision makers will need to make decisions regarding this technology - we need to produce resources which explain it, the benefits and the risks, particularly when compared with fine-tuning (or doing nothing), any of our relevant findings.

## Getting Started

> Tell the user how to get started (using a numbered list can be helpful). List one action per step with example code if possible.

1. Clone the repository. To learn about what this means, and how to use Git, see the [Git guide](https://nhsdigital.github.io/rap-community-of-practice/training_resources/git/using-git-collaboratively/).

```
git clone <insert URL>
```

2. Set up your environment, using [`pdm`](https://github.com/pdm-project/pdm)

3. Create your own `.secrets` file with relevant keys (see [`.secrets_example`](.secrets_example)) for the format.

4. Open the [`dev.ipynb`](dev.ipynb) and run it

## Project structure

> Provide the user with an outline of your repository structure. This template is primarily designed for publications teams at NHS England. Projects with different requirements (e.g. more complex documentation and modelling) should look to [DrivenData's cookiecutter project structure](https://drivendata.github.io/cookiecutter-data-science/#directory-structure), as well as our [Community of Practice](https://nhsdigital.github.io/rap-community-of-practice/training_resources/python/project-structure-and-packaging/) for guidance.

```text
|   .gitignore                        <- Files (& file types) automatically removed from version control for security purposes
|   config.toml                       <- Configuration file with parameters we want to be able to change (e.g. date)
|   environment.yml                   <- Conda equivalent of requirements file
|   requirements.txt                  <- Requirements for reproducing the analysis environment 
|   pyproject.toml                    <- Configuration file containing package build information
|   LICENCE                           <- License info for public distribution
|   README.md                         <- Quick start guide / explanation of your project
|
|   create_publication.py             <- Runs the overall pipeline to produce the publication     
|
+---src                               <- Scripts with functions for use in 'create_publication.py'. Contains project's codebase.
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |
|   +---utils                     <- Scripts relating to configuration and handling data connections e.g. importing data, writing to a database etc.
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |       file_paths.py             <- Configures file paths for the package
|   |       logging_config.py         <- Configures logging
|   |       data_connections.py       <- Handles data connections i.e. reading/writing dataframes from SQL Server
|   | 
|   +---processing                    <- Scripts with modules containing functions to process data i.e. clean and derive new fields
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |       clean.py                  <- Perform cleaning and wrangling processes 
|   |       derive_fields.py          <- Create new field definitions, columns, derivations.
|   | 
|   +---data_ingestion                <- Scripts with modules containing functions to preprocess read data i.e. perform validation/data quality checks, other preprocessing etc.
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |       preprocessing.py          <- Perform preprocessing, for example preparing your data for metadata or data quality checks.
|   |       validation_checks.py      <- Perform validation checks e.g. a field has acceptable values.
|   |
|   +---data_exports
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |       write_excel.py            <- Populates an excel .xlsx template with values from your CSV output.
|   |
+---sql                               <- SQL scripts for importing data  
|       example.sql
|
+---templates                         <- Templates for output files
|       publication_template.xlsx
|
+---tests
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |
|   +---backtests                     <- Comparison tests for the old and new pipeline's outputs
|   |       backtesting_params.py
|   |       test_compare_outputs.py
|   |       __init__.py               <- Makes the functions folder an importable Python module
|   |
|   +---unittests                     <- Tests for the functional outputs of Python code
|   |       test_data_connections.py
|   |       test_processing.py
|   |       __init__.py               <- Makes the functions folder an importable Python module
```

### `root`

In the highest level of this repository (known as the 'root'), there is one Python file: `create_publication.py`. This top level file should be the main place where users interact with the code, where you store the steps to create your publication.

This file currently runs a set of example steps using example data.

### `src`

This directory contains the meaty parts of the code. By organising the code into logical sections, we make it easier to understand, maintain and test. Moreover, tucking the complex code out of the way means that users don't need to understand everything about the code all at once.

* `data_connections.py` handles reading data in and writing data back out.
* `processing` folder contains the core business logic.
* `utils` folder contains useful reusable functions (e.g. to set up logging, and importing configuration settings from `config.toml`)
* `write_excel.py` contains functions relating to the final part of the pipeline, any exporting or templating happens here. This is a simplistic application of writing output code to an Excel spreadsheet template (.xlsx). A good example of this application is: [NHS sickness absence rates publication](https://github.com/NHSDigital/absence-rates). We highly recommend to use [Automated Excel Production](https://nhsd-git.digital.nhs.uk/data-services/analytics-service/iuod/automated-excel-publications) for a more in depth Excel template production application.

## Licence

> The [LICENCE](/LICENCE) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government 3.0 licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Acknowledgements
- [Connor Quinn](https://github.com/connor1q)
- [Sam Hollings](https://github.com/SamHollings)
- [Maakhe Ndhlela](https://github.com/maakhe)
- [Harriet Sands](https://github.com/harrietrs)
- [Xiyao Zhuang](https://github.com/xiyaozhuang)
- [Helen Richardson](https://github.com/helrich)
- [The RAP team](https://github.com/NHSDigital/rap-community-of-practice)!
