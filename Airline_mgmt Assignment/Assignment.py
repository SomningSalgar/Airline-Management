from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window

if __name__ == '__main__':
    spark=SparkSession.builder.appName("Airline Data Management").master("local[*]").getOrCreate()

                                   ## Airline Data

    airline_schema = StructType([StructField("Airline_id", IntegerType()),
                                StructField("Name", StringType()),
                                StructField("Alias", StringType()),
                                StructField("IATA", StringType()),
                                StructField("ICAO", StringType()),
                                StructField("Callsign", StringType()),
                                StructField("Country", StringType()),
                                StructField("Active", StringType())
                                 ])
    airline_df = spark.read.csv(path=r"C:\Users\Vishalya\PycharmProjects\PysparkAirLineDataMangement\Input\airline.csv",
             schema=airline_schema)

                                     ## Airport Data

    aiport_schema = StructType([StructField("Airport_id", IntegerType()),
                                StructField("Name_Airport", StringType()),
                                StructField("City", StringType()),
                                StructField("Country", StringType()),
                                StructField("IATA_code", IntegerType()),
                                StructField("ICAO_Code", IntegerType()),
                                StructField("Latitude", DecimalType()),
                                StructField("Longitude", DecimalType()),
                                StructField("Altitude", IntegerType()),
                                StructField("Timezon", DecimalType()),
                                StructField("DST", StringType()),
                                StructField("Tz", StringType()),
                                StructField("Type_of_AP", StringType()),
                                StructField("Source", StringType())
                                ])

    airport_df = spark.read.csv(path=r"C:\Users\Vishalya\PycharmProjects\PysparkAirLineDataMangement\Input\airport.csv",
             schema=aiport_schema)

                                         ## Route data

    route_df = spark.read.parquet(r"C:\Users\Vishalya\PycharmProjects\PysparkAirLineDataMangement\Input\routes.snappy.parquet")


                                         ## Plane data

    plane_df = spark.read.options(delimiter="").csv(
        r"C:\Users\Vishalya\PycharmProjects\PysparkAirLineDataMangement\Input\plane.csv.gz", header=True)


        ## --->Q.(1) Replace \N or Null values if its integer col then by -1 & if its string col then by (Unknown)

    airline_df1 = airline_df.na.fill("(Unknown)").na.replace(("\\N"), "(Unknown)")
    # airline_df1.show()
    airport_df1 = airport_df.na.fill(value=-1)
    # airport_df1.show()
    route_df1 = route_df.withColumn("codeshare",when(route_df.codeshare.isNull(), "(Unknown)")
                                    .otherwise("codeshare")).na.replace("\\N", "(Unknown)")
    # route_df1.show()
    plane_df1=plane_df.na.replace("\\N", "(Unknown)")
    # plane_df1.show()

        ## creating TempView for SQL query
    airline_df1.createOrReplaceTempView("airline")
    airport_df1.createOrReplaceTempView("airport")
    route_df1.createOrReplaceTempView("route")


          ##--->Q.(2) Find country name which is having both airline and airport --total 198 country

    ## By using DF method -inner join
    # airport_df1.join(airline_df1,on="Country",how="inner").select(airport_df1.Country.alias("comm_countries"))\
    #     .distinct().orderBy("comm_countries").show()

    ## BY SQL
    # spark.sql("select distinct(ap.Country) from airline ai,airport ap where ai.Country=ap.Country order by ap.Country").show()


          ## ----> Q.(3) Get airline details like name,id  which has taken off more than 3 times from same airport--3558

    ## By DF
    # airline_df1.join(route_df1, on="Airline_id", how="inner").groupBy("Airline_id", "Name", "src_airport")\
    #     .agg(count("src_airport").alias("takeoff")).filter(col("takeoff")>3).orderBy(col("takeoff")).show()

    ## By SQL
    # spark.sql("select ai.Airline_id,ai.Name,src_airport,count(*) takeoff from airline ai inner join route rt on ai.Airline_id=rt.airline_id " +
    #           "group by ai.Airline_id,ai.Name,src_airport having count(*)>3 order by takeoff").show(3558)


           ## ----> Q.(4) Get airport details which has minimum number of takeoffs and landing.

                      ## For takeoff--src_airport
    # takeoff=airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id,"inner")\
    #     .groupBy("Airport_id","Name_Airport","src_airport").count()

    # mini=takeoff.agg(min("count")).take(1)[0][0]
    # takeoff.filter(col("count")==mini).show()

                    ## For landing ----dest_airport
    # landing = airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id, "inner")\
    #     .groupBy("Airport_id", "Name_Airport", "dest_airport").count()
    # mini = landing.agg(min("count")).take(1)[0][0]
    # landing.select("Airport_id", "Name_Airport", "dest_airport","count").filter(col("count")==mini).show()

    #DF Single query-
    # airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id, "inner")\
    # .groupBy("Airport_id","Name_Airport","src_airport","dest_airport")\
    # .agg(count("src_airport").alias("takeoff"),count("dest_airport").alias("landing"))\
    # .orderBy(col("takeoff").asc(),col("landing").asc()).limit(1).show()


    ## By sql
    # spark.sql("select Airport_id,Name_Airport,src_airport,dest_airport,count(src_airport) takeoff,count(dest_airport) landing "+
    #           "from airport ap inner join route rt on Airport_id=src_airport_id " +
    #           "group by Airport_id,Name_Airport,src_airport,dest_airport " +
    #           "order by takeoff asc,landing asc").show()



          ##-----> Q(5). get airport details which is having maximum number of takeoff and landing.

                      ## For takeoff--src_airport
    # takeoff=airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id,"inner")\
    #     .groupBy("Airport_id","Name_Airport","src_airport").count()
    #
    # maxi=takeoff.agg(max("count")).take(1)[0][0]
    # takeoff.filter(col("count")==maxi).show()

                    ## For landing ----dest_airport
    # landing = airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id, "inner")\
    #     .groupBy("Airport_id", "Name_Airport", "dest_airport").count()
    #
    # maxi = landing.agg(max("count")).take(1)[0][0]
    # landing.select("Airport_id", "Name_Airport", "dest_airport","count").filter(col("count")==maxi).show()

    ## DF Single query
    # airport_df1.join(route_df1, airport_df1.Airport_id == route_df1.src_airport_id, "inner") \
    #     .groupBy("Airport_id", "Name_Airport", "src_airport", "dest_airport") \
    #     .agg(count("src_airport").alias("takeoff"), count("dest_airport").alias("landing")) \
    #     .orderBy(col("takeoff").desc(), col("landing").desc()).limit(1).show()

    ## By SQL
    # spark.sql("select Airport_id,Name_Airport,src_airport,dest_airport,count(src_airport) takeoff,count(dest_airport) landing "+
    #           "from airport ap inner join route rt on Airport_id=src_airport_id " +
    #           "group by Airport_id,Name_Airport,src_airport,dest_airport " +
    #           "order by takeoff desc,landing desc").show()


        ##-----> (6). Get the airline details, which is having direct flights.
                    # details like airline id, name, source airport name, and destination airport name

    ## By DF
    # airline_df1.join(route_df1,on="Airline_id",how="inner")\
    #     .select("Airline_id","Name","src_airport","dest_airport","stops").filter(col("stops")=0).show()

    ## By SQL
    # spark.sql("select ai.Airline_id,Name,src_airport,dest_airport,stops "+
    #           "from airline ai inner join route rt on ai.airline_id=rt.airline_id where stops=0").show()
