from statistics import mean

with open("Logging/pub_start_logger.csv", 'r') as logging_file:
    contents = logging_file.read()
    start_timestamp = contents.split(',')
    start_timestamp.pop()
    start_timestamp = [int(x) for x in start_timestamp]
    print(start_timestamp)

with open("Logging/pub_recv_logger.csv", 'r') as logging_file:
    contents = logging_file.read()
    end_timestamp = contents.split(',')
    end_timestamp.pop()
    end_timestamp = [int(x) for x in end_timestamp]
    print (end_timestamp)

with open("Logging/final_time.csv", 'a') as logging_file:
    max_len = min(len(start_timestamp), len(end_timestamp))
    average_result = []
    for i in range(max_len):
        diff = (end_timestamp[i]-start_timestamp[i]) / 1000
        average_result.append(diff)
        logging_file.write(str(diff) + ', ')

    logging_file.write('\n')

with open("Logging/avg_time.csv", 'a') as logging_file:
    logging_file.write(str(mean(average_result))+'\n')
