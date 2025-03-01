# Pipeline d'Analyse du Marché des Cryptomonnaies

## Description
Ce projet est une pipeline d'analyse des données du marché des cryptomonnaies en utilisant Apache Airflow pour l'orchestration, Hadoop HDFS pour le stockage brut, Hadoop MapReduce pour le traitement des données, et HBase pour le stockage structuré. Il collecte les données en temps réel via l'API CoinGecko, les traite, et les stocke pour une analyse ultérieure.

## Objectifs
- Automatiser la collecte et le traitement des données des cryptomonnaies.
- Utiliser des technologies Big Data (HDFS, MapReduce, HBase) pour gérer de grands volumes de données.
- Fournir une interface via Airflow pour surveiller et planifier les tâches.

## Prérequis
Pour exécuter ce projet, vous aurez besoin de :

- **Docker** et **Docker Compose** (pour déployer Airflow, HDFS, HBase, etc.).
- **Git** (pour cloner le dépôt).
- Une connexion Internet (pour accéder à l'API CoinGecko).
- Python 3.8+ avec les dépendances listées dans `requirements.txt`.

## Installation

### 1. Clonez le dépôt
Cloner ce dépôt sur votre machine locale :
```bash
git clone git@github.com:elkhdarABDELHAMID/Pipeline-d-Analyse-du-March-des-Cryptomonnaies.git
cd Pipeline-d-Analyse-du-March-des-Cryptomonnaies
