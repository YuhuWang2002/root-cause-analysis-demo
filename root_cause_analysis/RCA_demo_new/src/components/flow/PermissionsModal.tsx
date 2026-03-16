import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFlowStore } from '@/stores/flowStore';
import { Button } from '@/components/common/Button';

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: {
    create: boolean;
    edit: boolean;
    delete: boolean;
    view: boolean;
    export: boolean;
  };
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

const defaultRoles: Role[] = [
  {
    id: 'admin',
    name: '管理员',
    description: '拥有所有权限',
    permissions: { create: true, edit: true, delete: true, view: true, export: true },
  },
  {
    id: 'analyst',
    name: '分析员',
    description: '可以创建和编辑分析',
    permissions: { create: true, edit: true, delete: false, view: true, export: true },
  },
  {
    id: 'viewer',
    name: '查看者',
    description: '只能查看分析结果',
    permissions: { create: false, edit: false, delete: false, view: true, export: false },
  },
];

export default function PermissionsModal({ isOpen, onClose }: Props) {
  const { currentProjectId, projectsData, updateProjectPermissions } = useFlowStore();
  const [roles, setRoles] = useState<Role[]>(defaultRoles);
  const [selectedRole, setSelectedRole] = useState<string>('admin');

  const handleSave = () => {
    if (currentProjectId) {
      updateProjectPermissions(currentProjectId, { roles });
    }
    onClose();
  };

  const handlePermissionChange = (roleId: string, permission: keyof Role['permissions'], value: boolean) => {
    setRoles(roles.map(role => 
      role.id === roleId 
        ? { ...role, permissions: { ...role.permissions, [permission]: value } }
        : role
    ));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-gray-800 rounded-xl p-6 w-[600px] border border-gray-700 max-h-[80vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">权限配置</h3>
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-white font-medium mb-3">角色列表</h4>
                <div className="space-y-2">
                  {roles.map(role => (
                    <div
                      key={role.id}
                      onClick={() => setSelectedRole(role.id)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedRole === role.id 
                          ? 'bg-primary/20 border border-primary' 
                          : 'bg-gray-700 border border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h5 className="text-white font-medium">{role.name}</h5>
                          <p className="text-xs text-gray-400">{role.description}</p>
                        </div>
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-white font-medium mb-3">
                  {roles.find(r => r.id === selectedRole)?.name} - 权限配置
                </h4>
                <div className="bg-gray-700 rounded-lg p-4 space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-gray-300">创建</span>
                    <input
                      type="checkbox"
                      checked={roles.find(r => r.id === selectedRole)?.permissions.create || false}
                      onChange={(e) => handlePermissionChange(selectedRole, 'create', e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500 text-primary focus:ring-primary"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-gray-300">编辑</span>
                    <input
                      type="checkbox"
                      checked={roles.find(r => r.id === selectedRole)?.permissions.edit || false}
                      onChange={(e) => handlePermissionChange(selectedRole, 'edit', e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500 text-primary focus:ring-primary"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-gray-300">删除</span>
                    <input
                      type="checkbox"
                      checked={roles.find(r => r.id === selectedRole)?.permissions.delete || false}
                      onChange={(e) => handlePermissionChange(selectedRole, 'delete', e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500 text-primary focus:ring-primary"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-gray-300">查看</span>
                    <input
                      type="checkbox"
                      checked={roles.find(r => r.id === selectedRole)?.permissions.view || false}
                      onChange={(e) => handlePermissionChange(selectedRole, 'view', e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500 text-primary focus:ring-primary"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-gray-300">导出</span>
                    <input
                      type="checkbox"
                      checked={roles.find(r => r.id === selectedRole)?.permissions.export || false}
                      onChange={(e) => handlePermissionChange(selectedRole, 'export', e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500 text-primary focus:ring-primary"
                    />
                  </label>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="ghost" onClick={onClose}>取消</Button>
              <Button onClick={handleSave}>保存配置</Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
