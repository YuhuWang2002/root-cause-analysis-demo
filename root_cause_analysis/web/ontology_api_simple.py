"""
简化的本体API服务器（不依赖FastAPI）

提供本体的简单HTTP接口，支持：
- 查询本体实体
- 查询本体关系
- 查询本体属性
- 获取本体完整信息
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# 添加web目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ontology_manager import load_ontology_from_file


class OntologyAPIHandler(BaseHTTPRequestHandler):
    """本体API请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ontology_manager = None
    
    def load_ontology(self):
        """加载本体"""
        if self.ontology_manager is None:
            try:
                self.ontology_manager = load_ontology_from_file("ontology.json")
                print(f"[API] 本体加载成功: {len(self.ontology_manager.entities)} 个实体")
            except Exception as e:
                print(f"[API] 加载本体失败: {str(e)}")
                self.ontology_manager = None
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code, 'application/json', json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def send_error_response(self, message, status_code=400):
        """发送错误响应"""
        self.send_json_response({"error": message}, status_code)
    
    def do_GET(self):
        """处理GET请求"""
        self.load_ontology()
        
        if self.ontology_manager is None:
            self.send_error_response("本体加载失败", 500)
            return
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 根路径
        if path == '/' or path == '':
            self.send_json_response({
                "message": "本体管理API（简化版）",
                "version": "1.0.0",
                "endpoints": {
                    "GET /entities": "获取所有实体",
                    "GET /relations": "获取所有关系",
                    "GET /attributes": "获取所有属性",
                    "GET /ontology": "获取完整本体信息"
                }
            })
        
        # 获取所有实体
        elif path == '/entities':
            entities = []
            for entity in self.ontology_manager.entities.values():
                entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "description": entity.description,
                    "attributes": entity.attributes
                })
            self.send_json_response({"entities": entities})
        
        # 获取所有关系
        elif path == '/relations':
            relations = []
            for relation in self.ontology_manager.relations:
                relations.append({
                    "source": relation.source,
                    "target": relation.target,
                    "relation_type": relation.relation_type,
                    "weight": relation.weight,
                    "description": relation.description
                })
            self.send_json_response({"relations": relations})
        
        # 获取所有属性
        elif path == '/attributes':
            attributes = []
            for attr in self.ontology_manager.attributes.values():
                attributes.append({
                    "name": attr.name,
                    "type": attr.type,
                    "description": attr.description,
                    "default_value": attr.default_value,
                    "range": list(attr.range) if attr.range else None,
                    "enum_values": attr.enum_values
                })
            self.send_json_response({"attributes": attributes})
        
        # 获取完整本体信息
        elif path == '/ontology':
            entities = []
            for entity in self.ontology_manager.entities.values():
                entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "description": entity.description,
                    "attributes": entity.attributes
                })
            
            relations = []
            for relation in self.ontology_manager.relations:
                relations.append({
                    "source": relation.source,
                    "target": relation.target,
                    "relation_type": relation.relation_type,
                    "weight": relation.weight,
                    "description": relation.description
                })
            
            attributes = []
            for attr in self.ontology_manager.attributes.values():
                attributes.append({
                    "name": attr.name,
                    "type": attr.type,
                    "description": attr.description,
                    "default_value": attr.default_value,
                    "range": list(attr.range) if attr.range else None,
                    "enum_values": attr.enum_values
                })
            
            self.send_json_response({
                "entities": entities,
                "relations": relations,
                "attributes": attributes,
                "description": f"当前本体包含 {len(entities)} 个实体，{len(relations)} 个关系，{len(attributes)} 个属性"
            })
        
        else:
            self.send_error_response(f"未知的路径: {path}", 404)
    
    def log_message(self, format, *args):
        """记录日志"""
        print(f"[API] {format % args}")


def run_server(host='0.0.0.0', port=8000):
    """启动服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, OntologyAPIHandler)
    
    print("="*60)
    print("本体API服务器（简化版）")
    print("="*60)
    print(f"服务器地址: http://{host}:{port}")
    print(f"本体文件: ontology.json")
    print(f"按 Ctrl+C 停止服务器")
    print("="*60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[API] 服务器已停止")
        httpd.server_close()


if __name__ == "__main__":
    run_server()