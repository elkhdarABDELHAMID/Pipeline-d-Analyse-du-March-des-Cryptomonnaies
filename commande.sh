#intialiser base de donnes
docker-compose run --rm airflow-webserver airflow db init

docker-compose run --rm airflow-scheduler airflow db init




docker exec -it airflow-webserver airflow users create --username admin --firstname elkhdar --lastname abdelhamid --role Admin --email admin@example.com --password admin


hdfs dfs -chown dr.who:supergroup /



docker run big_data_projet-scraper bash -c "python /app/scraper.py"

docker run -it big_data_projet-mapreduce bash


docker exec -u root -it hadoop-namenode bash
git push -u origin main


docker system prune -a --volumes