#include "json_utils.hpp"
#include <dbforge/exceptions.hpp>
#include <json/json.h>
#include <sstream>

namespace dbforge {
namespace json_utils {

Json::Value parse_json(const std::string& json_str) {
    Json::Value root;
    Json::CharReaderBuilder builder;
    std::string errors;
    
    std::istringstream stream(json_str);
    if (!Json::parseFromStream(builder, stream, &root, &errors)) {
        throw Exception("Failed to parse JSON: " + errors);
    }
    
    return root;
}

std::string to_json_string(const Json::Value& json) {
    Json::StreamWriterBuilder builder;
    builder["indentation"] = "";  // Compact output
    return Json::writeString(builder, json);
}

Json::Value row_to_json(const Row& row) {
    Json::Value json_row(Json::objectValue);
    for (const auto& pair : row) {
        json_row[pair.first] = pair.second;
    }
    return json_row;
}

Row json_to_row(const Json::Value& json) {
    Row row;
    if (json.isObject()) {
        for (const auto& key : json.getMemberNames()) {
            row[key] = json[key].asString();
        }
    }
    return row;
}

Json::Value rows_to_json(const std::vector<Row>& rows) {
    Json::Value json_array(Json::arrayValue);
    for (const auto& row : rows) {
        json_array.append(row_to_json(row));
    }
    return json_array;
}

std::vector<Row> json_to_rows(const Json::Value& json) {
    std::vector<Row> rows;
    if (json.isArray()) {
        for (const auto& item : json) {
            rows.push_back(json_to_row(item));
        }
    }
    return rows;
}

Json::Value column_to_json(const Column& column) {
    Json::Value json_col(Json::objectValue);
    json_col["name"] = column.name;
    json_col["type"] = column.type;
    if (column.primary_key) {
        json_col["primary_key"] = true;
    }
    if (column.not_null) {
        json_col["not_null"] = true;
    }
    if (!column.default_value.empty()) {
        json_col["default"] = column.default_value;
    }
    if (column.unique) {
        json_col["unique"] = true;
    }
    return json_col;
}

Json::Value columns_to_json(const std::vector<Column>& columns) {
    Json::Value json_array(Json::arrayValue);
    for (const auto& column : columns) {
        json_array.append(column_to_json(column));
    }
    return json_array;
}

Json::Value params_to_json(const Params& params) {
    Json::Value json_array(Json::arrayValue);
    for (const auto& param : params) {
        json_array.append(param);
    }
    return json_array;
}

void check_error_response(int status_code, const Json::Value& json) {
    if (status_code >= 400) {
        std::string message = "HTTP " + std::to_string(status_code);
        std::string error_code;
        
        if (json.isMember("error")) {
            const Json::Value& error = json["error"];
            if (error.isMember("message")) {
                message = error["message"].asString();
            }
            if (error.isMember("code")) {
                error_code = error["code"].asString();
            }
        }
        
        if (status_code == 404) {
            throw DatabaseNotFound(message, status_code, error_code);
        } else if (status_code == 400) {
            throw InvalidRequest(message, status_code, error_code);
        } else if (status_code == 401) {
            throw AuthenticationError(message, status_code, error_code);
        } else if (status_code >= 500) {
            throw ServerError(message, status_code, error_code);
        } else {
            throw Exception(message, status_code, error_code);
        }
    }
}

SpawnResult parse_spawn_result(const Json::Value& json) {
    SpawnResult result;
    result.message = json.get("message", "").asString();
    result.database_name = json.get("db_name", "").asString();
    result.container_id = json.get("container_id", "").asString();
    return result;
}

PruneResult parse_prune_result(const Json::Value& json) {
    PruneResult result;
    result.message = json.get("message", "").asString();
    result.database_name = json.get("db_name", "").asString();
    return result;
}

std::vector<DatabaseInfo> parse_database_list(const Json::Value& json) {
    std::vector<DatabaseInfo> databases;
    if (json.isArray()) {
        for (const auto& item : json) {
            DatabaseInfo db_info;
            db_info.name = item.get("name", "").asString();
            db_info.container_id = item.get("container_id", "").asString();
            db_info.status = item.get("status", "").asString();
            databases.push_back(db_info);
        }
    }
    return databases;
}

HealthResult parse_health_result(const Json::Value& json) {
    HealthResult result;
    result.message = json.get("message", "").asString();
    result.status = json.get("status", "").asString();
    result.version = json.get("version", "").asString();
    return result;
}

QueryResult parse_query_result(const Json::Value& json) {
    QueryResult result;
    result.message = json.get("message", "").asString();
    result.rows_affected = json.get("rows_affected", 0).asInt();
    
    if (json.isMember("data")) {
        result.data = json_to_rows(json["data"]);
    }
    
    return result;
}

CreateTableResult parse_create_table_result(const Json::Value& json) {
    CreateTableResult result;
    result.message = json.get("message", "").asString();
    
    // Extract table name from message if available
    std::string msg = result.message;
    size_t start = msg.find("'");
    if (start != std::string::npos) {
        size_t end = msg.find("'", start + 1);
        if (end != std::string::npos) {
            result.table_name = msg.substr(start + 1, end - start - 1);
        }
    }
    
    return result;
}

InsertResult parse_insert_result(const Json::Value& json) {
    InsertResult result;
    result.message = json.get("message", "").asString();
    result.rows_affected = json.get("rows_affected", 0).asInt();
    return result;
}

DropResult parse_drop_result(const Json::Value& json) {
    DropResult result;
    result.message = json.get("message", "").asString();
    return result;
}

std::vector<ColumnInfo> parse_column_info(const Json::Value& json) {
    std::vector<ColumnInfo> columns;
    if (json.isMember("data") && json["data"].isArray()) {
        for (const auto& item : json["data"]) {
            ColumnInfo col_info;
            col_info.cid = item.get("cid", 0).asInt();
            col_info.name = item.get("name", "").asString();
            col_info.type = item.get("type", "").asString();
            col_info.not_null = item.get("notnull", 0).asInt() != 0;
            col_info.default_value = item.get("dflt_value", "").asString();
            col_info.primary_key = item.get("pk", 0).asInt() != 0;
            columns.push_back(col_info);
        }
    }
    return columns;
}

std::vector<std::string> parse_table_list(const Json::Value& json) {
    std::vector<std::string> tables;
    if (json.isMember("data") && json["data"].isArray()) {
        for (const auto& item : json["data"]) {
            if (item.isMember("name")) {
                tables.push_back(item["name"].asString());
            }
        }
    }
    return tables;
}

} // namespace json_utils
} // namespace dbforge