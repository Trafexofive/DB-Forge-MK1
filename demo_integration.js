#!/usr/bin/env node

/**
 * DB-Forge Frontend-Backend Integration Demo
 * 
 * This script demonstrates the working integration between 
 * the DB-Forge frontend and backend services.
 */

const API_BASE_URL = 'http://localhost:8081'
const API_KEY = 'development-api-key-12345'

async function makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Host': 'db.localhost',  // Required for Traefik routing
            'X-API-Key': API_KEY,
            ...options.headers,
        },
    })

    if (!response.ok) {
        const text = await response.text()
        throw new Error(`HTTP ${response.status}: ${text}`)
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
        return await response.json()
    } else {
        return await response.text()
    }
}

async function demonstrateIntegration() {
    console.log('🌟 DB-Forge Frontend-Backend Integration Demo')
    console.log('============================================\n')
    
    try {
        // Demo 1: System Health
        console.log('🔍 1. System Health Check')
        const stats = await makeRequest('/admin/gateway/stats')
        console.log(`   📊 System Uptime: ${Math.floor(stats.uptime_seconds)}s`)
        console.log(`   📈 Total API Requests: ${stats.total_requests}`)
        console.log(`   ❌ Total Errors: ${stats.total_errors}`)
        console.log('   ✅ Backend API is responsive and healthy')
        
        // Demo 2: Database Management
        console.log('\n🗄️  2. Database Management')
        let databases = await makeRequest('/admin/databases')
        console.log(`   📁 Current databases: ${databases.length}`)
        
        if (databases.length > 0) {
            databases.forEach(db => {
                console.log(`      - ${db.name} (${db.status})`)
            })
        }
        
        // Demo 3: Create a demo database
        console.log('\n🆕 3. Creating Demo Database')
        const demoDbName = `demo-${Date.now()}`
        console.log(`   🏗️  Creating database: ${demoDbName}`)
        
        const createResult = await makeRequest(`/admin/databases/spawn/${demoDbName}`, {
            method: 'POST'
        })
        
        console.log(`   ✅ Successfully created: ${createResult.db_name}`)
        console.log(`   📦 Container ID: ${createResult.container_id.substring(0, 12)}...`)
        
        // Demo 4: Database Operations
        console.log('\n💾 4. Database Operations')
        console.log('   🔧 Creating table structure...')
        
        await makeRequest(`/api/db/${demoDbName}/query`, {
            method: 'POST',
            body: JSON.stringify({
                sql: `CREATE TABLE demo_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );`,
                params: []
            })
        })
        
        console.log('   ✅ Table "demo_users" created')
        
        // Demo 5: Data Operations
        console.log('\n📝 5. Data Operations')
        const users = [
            ['Alice Johnson', 'alice@example.com'],
            ['Bob Smith', 'bob@example.com'], 
            ['Carol Davis', 'carol@example.com']
        ]
        
        for (const [name, email] of users) {
            await makeRequest(`/api/db/${demoDbName}/query`, {
                method: 'POST',
                body: JSON.stringify({
                    sql: 'INSERT INTO demo_users (name, email) VALUES (?, ?);',
                    params: [name, email]
                })
            })
            console.log(`   👤 Added user: ${name}`)
        }
        
        // Demo 6: Query Data
        console.log('\n📊 6. Querying Data')
        const queryResult = await makeRequest(`/api/db/${demoDbName}/query`, {
            method: 'POST',
            body: JSON.stringify({
                sql: 'SELECT id, name, email, created_at FROM demo_users ORDER BY id;',
                params: []
            })
        })
        
        console.log(`   📋 Found ${queryResult.data.length} users:`)
        queryResult.data.forEach(row => {
            console.log(`      ${row[0]}. ${row[1]} (${row[2]})`)
        })
        
        // Demo 7: Advanced Query
        console.log('\n🔍 7. Advanced Queries')
        const countResult = await makeRequest(`/api/db/${demoDbName}/query`, {
            method: 'POST',
            body: JSON.stringify({
                sql: 'SELECT COUNT(*) as user_count FROM demo_users WHERE email LIKE ?;',
                params: ['%@example.com']
            })
        })
        
        const userCount = countResult.data[0][0]
        console.log(`   📊 Users with @example.com emails: ${userCount}`)
        
        // Demo 8: Verify Integration
        console.log('\n🔄 8. Verifying Full Integration')
        const finalDbList = await makeRequest('/admin/databases')
        const ourDb = finalDbList.find(db => db.name === demoDbName)
        
        if (ourDb) {
            console.log(`   ✅ Database ${demoDbName} is running (${ourDb.status})`)
            console.log(`   🐳 Container: ${ourDb.container_id.substring(0, 12)}...`)
        }
        
        // Demo 9: Cleanup
        console.log('\n🗑️  9. Cleanup')
        console.log(`   🧹 Removing demo database: ${demoDbName}`)
        
        await makeRequest(`/admin/databases/prune/${demoDbName}`, {
            method: 'POST'
        })
        
        console.log('   ✅ Demo database removed')
        
        // Final Status
        console.log('\n🎉 Integration Demo Complete!')
        console.log('=====================================')
        console.log('✅ Backend API: Fully functional')
        console.log('✅ Database Management: Working')
        console.log('✅ SQL Operations: Working') 
        console.log('✅ Container Orchestration: Working')
        console.log('✅ Authentication: Working')
        console.log('')
        console.log('🌐 Frontend URL: http://frontend.db.localhost:8081')
        console.log('📚 API Docs: http://db.localhost:8081/docs')
        console.log('📊 Traefik Dashboard: http://localhost:8080/dashboard/')
        console.log('')
        console.log('🔑 API Key for testing: development-api-key-12345')
        
    } catch (error) {
        console.error('\n❌ Demo failed:', error.message)
        process.exit(1)
    }
}

// Check Node.js version for fetch support
if (typeof fetch === 'undefined') {
    console.error('❌ This script requires Node.js 18+ (includes fetch)')
    console.error('   Or install a fetch polyfill for older versions')
    process.exit(1)
}

demonstrateIntegration()