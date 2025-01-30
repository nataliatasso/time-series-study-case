# Study Case

### Problem statement

According to SCOD Brazil, when analyzing the profile of real estate market consumers, it was observed that the predominant age group, approximately 50%, falls between 38 and 58 years old. Based on this, we would like a time series analysis from 2007 to 2022 of the ratio of consumers in this age group to the number of active companies per state.

Use data from 2007 to 2020 to estimate values for 2021 and 2022. Additionally, group the time series to identify which states exhibited similar trends. We are interested in determining which states are more saturated and which present greater future opportunities.

### Data sources

The required data can be found in the following sources:

1. **Business Data**: Available in SIDRA's "Table 1757 - General data of construction companies, according to employment size categories".
    - API Documentation: [SIDRA API](https://sidra.ibge.gov.br/Tabela/1757)

2. **Population Data**: Estimated population data can be found in the ["População por sexo e idade simples"](data/projecoes_2024_tab1_idade_simples.xlsx) table, which was downloaded on January 27th, 2025.
    - Source: [Population Projection](https://www.ibge.gov.br/estatisticas/sociais/populacao/9109-projecao-da-populacao.html)

## How to run the project

1. Clone the repository:
   ```sh
   git clone https://github.com/nataliatasso/time-series-study-case.git
   cd time-series-study-case
   ```

2. Make sure you have Python installed.
3. All the dependencies are listed on [requirements.txt](requirements.txt). They can be installed using:
    ```sh
    pip install -r requirements.txt
    ``` 

4. Run the main script:
    ```sh
    python case_study.py
    ``` 