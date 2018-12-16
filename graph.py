import click
from google.cloud import bigquery

uni1 = 'mw3239' # Your uni
uni2 = 'tw2686' # Partner's uni. If you don't have a partner, put None

# Test function
def testquery(client):
    q = """select * from `w4111-columbia.graph.tweets` limit 3"""
    job = client.query(q)

    # waits for query to execute and return
    results = job.result()
    return list(results)

# SQL query for Question 1. You must edit this funtion.
# This function should return a list of IDs and the corresponding text.
def q1(client):
    q = """select id, text from `w4111-columbia.graph.tweets` where text LIKE '%going live%' AND text LIKE '%www.twitch%'"""
    job = client.query(q)

    results = job.result()
    return list(results)

# SQL query for Question 2. You must edit this funtion.
# This function should return a list of days and their corresponding average likes.
def q2(client):
    q = """select SUBSTR(create_time,1,3) AS day, AVG(like_num) AS avg_likes from `w4111-columbia.graph.tweets` GROUP BY day ORDER BY avg_likes DESC LIMIT 1"""
    job = client.query(q)
    results = job.result()

    return list(results)

# SQL query for Question 3. You must edit this funtion.
# This function should return a list of source nodes and destination nodes in the graph.
def q3(client):
    q = """CREATE OR REPLACE TABLE dataset.GRAPH AS
	SELECT DISTINCT src_table.src_username AS src,
         twitter_username AS dst
          FROM `w4111-columbia.graph.tweets` dst_table,
          (
            SELECT twitter_username AS src_username,
                    text AS src_text
             FROM `w4111-columbia.graph.tweets`
          )
          AS src_table
          WHERE dst_table.twitter_username = SUBSTR(REGEXP_EXTRACT(src_table.src_text,r"@[[:^blank:]]+"),2)
		AND dst_table.twitter_username <> src_table.src_username"""
    job = client.query(q) 

    return []

# SQL query for Question 4. You must edit this funtion.
# This function should return a list containing the twitter username of the users having the max indegree and max outdegree.
def q4(client):
    q = """SELECT G2.dst AS max_indegree, G1.src AS max_outdegree
	FROM 
	(SELECT src
	FROM dataset.GRAPH
	GROUP BY src
	ORDER BY count(dst) DESC
	Limit 1) AS G1,

	(SELECT dst
	FROM dataset.GRAPH
	GROUP BY dst
	ORDER BY count(src) DESC
	Limit 1) AS G2

	"""
    job = client.query(q)
    results = job.result()
    return list(results)

# SQL query for Question 5. You must edit this funtion.
# This function should return a list containing value of the conditional probability.
def q5(client):
    q = """
	WITH 
	indegree AS (SELECT 
	src as inuser,  
	COUNT(dst) AS num
	FROM dataset.GRAPH	
	GROUP BY src),

	likes AS (SELECT 
	twitter_username as tuser,
	AVG(like_num) AS count
	FROM `w4111-columbia.graph.tweets`
	GROUP BY twitter_username), 

	main AS (SELECT inuser as user,num as indeg_num, count as avg_likes
	FROM indegree, likes
	where inuser = tuser),

	popularity AS (
	SELECT user, indeg_num, avg_likes,
	CASE
	WHEN indeg_num < (SELECT AVG(indeg.count)
        	FROM (SELECT count(src) as count
	FROM dataset.GRAPH
	GROUP BY dst) as indeg) 
	  AND
	  avg_likes < (SELECT AVG(like_num) AS average
	FROM `w4111-columbia.graph.tweets`)

	THEN 'UNPOPULAR'
	WHEN indeg_num > (SELECT AVG(indeg.count)
		FROM (SELECT count(src) as count
	FROM dataset.GRAPH
	GROUP BY dst) as indeg) 
	AND
	avg_likes > (SELECT AVG(like_num) AS average
	FROM `w4111-columbia.graph.tweets` )
	THEN 'POPULAR'
	ELSE ''
	END AS popular_unpopular

	FROM main
	),

	unpop_mention_pop AS (SELECT count(*) as mention_and_unpop
	FROM popularity mentions, dataset.GRAPH, popularity popular
	WHERE
		mentions.user = src
	AND	popular.user = dst
	AND popular.popular_unpopular = 'POPULAR'
	AND	mentions.popular_unpopular = 'UNPOPULAR'),

	total_unpop AS (SELECT count(*) as unpop
	FROM popularity
	WHERE	popular_unpopular = 'UNPOPULAR')

	SELECT mention_and_unpop/unpop as popular_unpopular
	FROM unpop_mention_pop, total_unpop

	"""
    job = client.query(q)
    results = job.result()

    return list(results)

# SQL query for Question 6. You must edit this funtion.
# This function should return a list containing the value for the number of triangles in the graph.
def q6(client):
    q = """
	select count(*)/3  as no_of_triangles
	from (select DISTINCT quer_1.A, quer_1.B, c.src as C
	from dataset.GRAPH as c, (select DISTINCT a.src as A, b.src as B, a.dst as A_dst
                          from dataset.GRAPH as a, dataset.GRAPH as b
                          where a.src = b.dst) as quer_1
	where quer_1.B = c.dst
	  AND quer_1.B != A_dst
	  AND c.src = A_dst)
	"""
    job = client.query(q)
    results = job.result()

    return list(results)

# SQL query for Question 7. You must edit this funtion.
# This function should return a list containing the twitter username and their corresponding PageRank.
def q7(client):
    q1 = """
         CREATE OR REPLACE TABLE dataset.PR AS
         WITH
	outbound as (select node_list, count(a.dst) as out_count
	from dataset.GRAPH as a, 
        	  (SELECT node as node_list
	          FROM
	          (select src as node from dataset.GRAPH
	          UNION DISTINCT
	          Select dst as node from dataset.GRAPH) as nodes) 
	where a.src = node_list
	group by node_list),
	
	pr as (select 1/count(*) as val
	from (select src
	  from dataset.GRAPH
	  UNION
	  DISTINCT select dst
	  from dataset.GRAPH)),
	  
	users as (SELECT nodes as user
	from (select src as nodes
	  from dataset.GRAPH
	  UNION
	  DISTINCT select dst as nodes
	  from dataset.GRAPH)),
	  
	pr_init as( 
	SELECT user, CAST(outbound.out_count as FLOAT64) as out_count, pr.val as pr_i, (pr.val/out_count) as pr_over_l
	FROM users, pr
	LEFT OUTER JOIN outbound
	ON user = outbound.node_list)

	select *
	from pr_init

         """
    job = client.query(q1)
    results = job.result()

    for i in range(20):
   	print("Step %d..." % (i+1))
   	q2 = """
   	     CREATE OR REPLACE TABLE dataset.PR AS
	     
             WITH
		outbound as (select node_list, count(a.dst) as out_count
		from dataset.GRAPH as a, 
	          (SELECT node as node_list
        	  FROM
	          (select src as node from dataset.GRAPH
        	  UNION DISTINCT
	          Select dst as node from dataset.GRAPH) as nodes) 
	where a.src = node_list
	group by node_list),
  
	users as (SELECT nodes as user
	from (select src as nodes
	  from dataset.GRAPH
	  UNION
	  DISTINCT select dst as nodes
	  from dataset.GRAPH)),
  
	pr_init as( 
	SELECT users.user, CAST(outbound.out_count as FLOAT64) as out_count, 
	pr_new.pr_i as new_pr_i , (pr_new.pr_i /outbound.out_count) as pr_over_l
	FROM users
	LEFT OUTER JOIN outbound
	ON user = outbound.node_list
	INNER JOIN dataset.PR AS pr_new
	ON users.user = pr_new.user),

	both_pr as (select dst as user, sum(pr_over_l) as pr_i
	from dataset.GRAPH, pr_init
	where src = user
	GROUP BY dst) 

	select *
	from both_pr
	ORDER BY pr_i DESC
	     """
	job = client.query(q2)
	results = job.result()
	

    q3 = """
	 select user as twitter_username, pr_i as rank_page_score
         from dataset.PR
         order by rank_page_score DESC
         LIMIT 100
         """
    job = client.query(q3)
    results = job.result()
    return list(results)


# Do not edit this function. This is for helping you develop your own iterative PageRank algorithm.
def bfs(client, start, n_iter):

    # You should replace dataset.bfs_graph with your dataset name and table name.
    q1 = """
        CREATE TABLE IF NOT EXISTS dataset.bfs_graph (src string, dst string);
        """
    q2 = """
        INSERT INTO dataset.bfs_graph(src, dst) VALUES
        ('A', 'B'),
        ('A', 'E'),
        ('B', 'C'),
        ('C', 'D'),
        ('E', 'F'),
        ('F', 'D'),
        ('A', 'F'),
        ('B', 'E'),
        ('B', 'F'),
        ('A', 'G'),
        ('B', 'G'),
        ('F', 'G'),
        ('H', 'A'),
        ('G', 'H'),
        ('H', 'C'),
        ('H', 'D'),
        ('E', 'H'),
        ('F', 'H');
        """

    job = client.query(q1)
    results = job.result()
    job = client.query(q2)
    results = job.result()

    # You should replace dataset.distances with your dataset name and table name. 
    q3 = """
        CREATE OR REPLACE TABLE dataset.distances AS
        SELECT '{start}' as node, 0 as distance
        """.format(start=start)
    job = client.query(q3)
    # Result will be empty, but calling makes the code wait for the query to complete
    job.result()

    for i in range(n_iter):
        print("Step %d..." % (i+1))
        q1 = """
        INSERT INTO dataset.distances(node, distance)
        SELECT distinct dst, {next_distance}
        FROM dataset.bfs_graph
            WHERE src IN (
                SELECT node
                FROM dataset.distances
                WHERE distance = {curr_distance}
                )
            AND dst NOT IN (
                SELECT node
                FROM dataset.distances
                )
            """.format(
                curr_distance=i,
                next_distance=i+1
            )
        job = client.query(q1)
        results = job.result()
        # print(results)


# Do not edit this function. You can use this function to see how to store tables using BigQuery.
def save_table():
    client = bigquery.Client()
    dataset_id = 'dataset'

    job_config = bigquery.QueryJobConfig()
    # Set use_legacy_sql to True to use legacy SQL syntax.
    job_config.use_legacy_sql = True
    # Set the destination table
    table_ref = client.dataset(dataset_id).table('test')
    job_config.destination = table_ref
    job_config.allow_large_results = True
    sql = """select * from [w4111-columbia.graph.tweets] limit 3"""

    # Start the query, passing in the extra configuration.
    query_job = client.query(
        sql,
        # Location must match that of the dataset(s) referenced in the query
        # and of the destination table.
        location='US',
        job_config=job_config)  # API request - starts the query

    query_job.result()  # Waits for the query to finish
    print('Query results loaded to table {}'.format(table_ref.path))

@click.command()
@click.argument("PATHTOCRED", type=click.Path(exists=True))
def main(pathtocred):
    client = bigquery.Client.from_service_account_json(pathtocred)

    funcs_to_test = [q1, q2, q3, q4, q5, q6, q7]
    #funcs_to_test = [testquery]
    for func in funcs_to_test:
        rows = func(client)
        print ("\n====%s====" % func.__name__)
        print(rows)

    #bfs(client, 'A', 5)

if __name__ == "__main__":
  main()
