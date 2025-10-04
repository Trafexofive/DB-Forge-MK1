#include <dbforge/database.hpp>
#include <dbforge/client.hpp>
#include <dbforge/exceptions.hpp>
#include "http_client.hpp"
#include "json_utils.hpp"
#include <json/json.h>
#include <sstream>

namespace dbforge {

Database::Database(Client& client, const std::string& name)
    : client_(client), name_(name), http_client_(*client.http_client_) {}

const std::string& Database::name() const {
    return name_;
}

CreateTableResult Database::create_table(const std::string& table_name, const std::vector<Column>& columns) {
    Json::Value json_data(Json::objectValue);
    json_data["table_name"] = table_name;
    json_data["columns"] = json_utils::columns_to_json(columns);
    
    std::string endpoint = "/api/db/" + name_ + "/tables";
    auto response = http_client_.request("POST", endpoint, json_utils::to_json_string(json_data));
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_create_table_result(json);
}

InsertResult Database::insert_rows(const std::string& table_name, const std::vector<Row>& rows) {
    Json::Value json_data(Json::objectValue);
    json_data["rows"] = json_utils::rows_to_json(rows);
    
    std::string endpoint = "/api/db/" + name_ + "/tables/" + table_name + "/rows";
    auto response = http_client_.request("POST", endpoint, json_utils::to_json_string(json_data));
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_insert_result(json);
}

std::vector<Row> Database::select_rows(const std::string& table_name, const Row& filters) {
    std::string endpoint = "/api/db/" + name_ + "/tables/" + table_name + "/rows";
    
    // Convert filters to query parameters
    std::map<std::string, std::string> params;
    for (const auto& filter : filters) {
        params[filter.first] = filter.second;
    }
    
    auto response = http_client_.request("GET", endpoint, "", params);
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    
    QueryResult result = json_utils::parse_query_result(json);
    return result.data;
}

QueryResult Database::execute_query(const std::string& sql, const Params& params) {
    Json::Value json_data(Json::objectValue);
    json_data["sql"] = sql;
    if (!params.empty()) {
        json_data["params"] = json_utils::params_to_json(params);
    }
    
    std::string endpoint = "/api/db/" + name_ + "/query";
    auto response = http_client_.request("POST", endpoint, json_utils::to_json_string(json_data));
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_query_result(json);
}

std::vector<std::string> Database::list_tables() {
    std::string sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'";
    QueryResult result = execute_query(sql);
    
    std::vector<std::string> tables;
    for (const auto& row : result.data) {
        auto it = row.find("name");
        if (it != row.end()) {
            tables.push_back(it->second);
        }
    }
    return tables;
}

std::vector<ColumnInfo> Database::get_table_schema(const std::string& table_name) {
    std::string sql = "PRAGMA table_info(" + table_name + ")";
    QueryResult result = execute_query(sql);
    
    std::vector<ColumnInfo> columns;
    for (const auto& row : result.data) {
        ColumnInfo col_info;
        
        auto cid_it = row.find("cid");
        if (cid_it != row.end()) {
            try {
                col_info.cid = std::stoi(cid_it->second);
            } catch (...) {
                col_info.cid = 0;
            }
        }
        
        auto name_it = row.find("name");
        if (name_it != row.end()) {
            col_info.name = name_it->second;
        }
        
        auto type_it = row.find("type");
        if (type_it != row.end()) {
            col_info.type = type_it->second;
        }
        
        auto notnull_it = row.find("notnull");
        if (notnull_it != row.end()) {
            col_info.not_null = (notnull_it->second == "1");
        }
        
        auto dflt_it = row.find("dflt_value");
        if (dflt_it != row.end()) {
            col_info.default_value = dflt_it->second;
        }
        
        auto pk_it = row.find("pk");
        if (pk_it != row.end()) {
            col_info.primary_key = (pk_it->second == "1");
        }
        
        columns.push_back(col_info);
    }
    
    return columns;
}

DropResult Database::drop_table(const std::string& table_name) {
    std::string sql = "DROP TABLE IF EXISTS " + table_name;
    execute_query(sql);
    
    DropResult result;
    result.message = "Table '" + table_name + "' dropped successfully.";
    result.table_name = table_name;
    return result;
}

QueryResult Database::update_rows(const std::string& table_name, 
                                 const Row& set_values, 
                                 const Row& where_conditions) {
    std::ostringstream sql;
    std::vector<std::string> params;
    
    sql << "UPDATE " << table_name << " SET ";
    
    // Build SET clause
    bool first = true;
    for (const auto& pair : set_values) {
        if (!first) sql << ", ";
        sql << pair.first << " = ?";
        params.push_back(pair.second);
        first = false;
    }
    
    // Build WHERE clause
    if (!where_conditions.empty()) {
        sql << " WHERE ";
        first = true;
        for (const auto& pair : where_conditions) {
            if (!first) sql << " AND ";
            sql << pair.first << " = ?";
            params.push_back(pair.second);
            first = false;
        }
    }
    
    return execute_query(sql.str(), params);
}

QueryResult Database::delete_rows(const std::string& table_name, const Row& where_conditions) {
    std::ostringstream sql;
    std::vector<std::string> params;
    
    sql << "DELETE FROM " << table_name;
    
    // Build WHERE clause
    if (!where_conditions.empty()) {
        sql << " WHERE ";
        bool first = true;
        for (const auto& pair : where_conditions) {
            if (!first) sql << " AND ";
            sql << pair.first << " = ?";
            params.push_back(pair.second);
            first = false;
        }
    }
    
    return execute_query(sql.str(), params);
}

} // namespace dbforge