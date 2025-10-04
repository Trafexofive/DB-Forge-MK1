#pragma once

#include <dbforge/types.hpp>
#include <json/json.h>
#include <string>
#include <vector>

namespace dbforge {
namespace json_utils {

// JSON parsing and serialization utilities

Json::Value parse_json(const std::string& json_str);
std::string to_json_string(const Json::Value& json);

// Row conversion
Json::Value row_to_json(const Row& row);
Row json_to_row(const Json::Value& json);
Json::Value rows_to_json(const std::vector<Row>& rows);
std::vector<Row> json_to_rows(const Json::Value& json);

// Column conversion
Json::Value column_to_json(const Column& column);
Json::Value columns_to_json(const std::vector<Column>& columns);

// Parameter conversion
Json::Value params_to_json(const Params& params);

// Error checking
void check_error_response(int status_code, const Json::Value& json);

// Result parsing
SpawnResult parse_spawn_result(const Json::Value& json);
PruneResult parse_prune_result(const Json::Value& json);
std::vector<DatabaseInfo> parse_database_list(const Json::Value& json);
HealthResult parse_health_result(const Json::Value& json);
QueryResult parse_query_result(const Json::Value& json);
CreateTableResult parse_create_table_result(const Json::Value& json);
InsertResult parse_insert_result(const Json::Value& json);
DropResult parse_drop_result(const Json::Value& json);
std::vector<ColumnInfo> parse_column_info(const Json::Value& json);
std::vector<std::string> parse_table_list(const Json::Value& json);

} // namespace json_utils
} // namespace dbforge