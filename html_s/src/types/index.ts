/* ═══════════════ Enums / Unions ═══════════════ */

export type RequestStatus = 'new' | 'in_progress' | 'completed' | 'rejected' | 'pending';
export type RequestPriority = 'low' | 'medium' | 'high' | 'critical';
export type UserRole = 'driver' | 'dispatcher' | 'admin';
export type VehicleStatus = 'active' | 'maintenance' | 'repair' | 'inactive';
export type NotificationType = 'maintenance' | 'urgent' | 'info' | 'reminder' | 'system';
export type FuelType = 'diesel' | 'petrol' | 'gas' | 'electric' | 'hybrid';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type ActivityAction =
  | 'request_created' | 'request_updated' | 'request_completed' | 'request_rejected'
  | 'mechanic_assigned' | 'vehicle_updated' | 'maintenance_planned' | 'maintenance_completed'
  | 'profile_updated' | 'user_login' | 'user_registered' | 'config_changed'
  | 'part_consumed' | 'part_restocked' | 'export_generated';
export type PartCategory = 'engine' | 'brakes' | 'suspension' | 'electrical' | 'body' | 'transmission' | 'filters' | 'fluids' | 'tires' | 'other';

/* ═══════════════ Core Models ═══════════════ */

export interface User {
  id: string;
  name: string;
  role: UserRole;
  email: string;
  phone: string;
  avatar?: string;
}

export interface Vehicle {
  id: string;
  plate: string;
  brand: string;
  model: string;
  year: number;
  vin: string;
  mileage: number;
  fuelType: FuelType;
  status: VehicleStatus;
  nextMaintenance: string;
  lastMaintenance?: string;
  assignedDriver?: string;
  assignedDriverId?: string;
  totalServiceCost: number;
  insuranceExpiry?: string;
  location?: GeoPoint;
  healthScore: number;       // 0-100
  riskLevel: RiskLevel;
  photo?: string;
}

export interface GeoPoint {
  lat: number;
  lng: number;
  address?: string;
  updatedAt: string;
}

export interface RepairRequest {
  id: string;
  vehicleId: string;
  vehiclePlate: string;
  driverName: string;
  driverId?: string;
  category: string;
  priority: RequestPriority;
  status: RequestStatus;
  description: string;
  createdAt: string;
  updatedAt: string;
  assignedTo?: string;
  slaDeadline?: string;
  slaBreached?: boolean;
  photoBefore?: string[];
  photoAfter?: string[];
  photos?: string[];
  mechanicComment?: string;
  repairSummary?: string;
  estimatedCost?: number;
  actualCost?: number;
  mileageAtCreation?: number;
  comments?: RequestComment[];
}

export interface RequestComment {
  id: string;
  authorId: string;
  authorName: string;
  authorRole: UserRole;
  text: string;
  createdAt: string;
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
  vehiclePlate?: string;
  link?: string;
  actorName?: string;
}

export interface MaintenanceTask {
  id: string;
  vehicleId: string;
  vehiclePlate: string;
  type: string;
  scheduledDate: string;
  completedDate?: string;
  status: 'scheduled' | 'overdue' | 'completed' | 'in_progress';
  description: string;
  estimatedCost?: number;
  actualCost?: number;
  assignedTo?: string;
  mileageAtService?: number;
}

/* ═══════════════ Activity Log ═══════════════ */

export interface ActivityLogEntry {
  id: string;
  action: ActivityAction;
  actorId: string;
  actorName: string;
  actorRole: UserRole;
  targetType: 'request' | 'vehicle' | 'maintenance' | 'user' | 'part' | 'system';
  targetId?: string;
  targetLabel?: string;
  details: string;
  timestamp: string;
}

/* ═══════════════ Spare Parts ═══════════════ */

export interface SparePart {
  id: string;
  name: string;
  partNumber: string;
  category: PartCategory;
  stockCount: number;
  minStock: number;
  unitCost: number;
  supplier: string;
  location?: string;
  lastRestocked?: string;
  compatibleVehicles?: string[];
}

export interface PartUsageRecord {
  id: string;
  partId: string;
  partName: string;
  requestId?: string;
  vehicleId: string;
  vehiclePlate: string;
  quantity: number;
  cost: number;
  usedAt: string;
  usedBy: string;
}

/* ═══════════════ Risk / Prediction ═══════════════ */

export interface VehicleHealthReport {
  vehicleId: string;
  healthScore: number;
  riskLevel: RiskLevel;
  factors: HealthFactor[];
  recommendations: string[];
  lastUpdated: string;
}

export interface HealthFactor {
  label: string;
  score: number;      // 0-100
  weight: number;     // 0-1
  status: 'good' | 'warning' | 'critical';
  detail: string;
}

/* ═══════════════ Analytics ═══════════════ */

export interface KpiData {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
}

export interface ChartDataPoint {
  month: string;
  total: number;
  completed: number;
}

export interface CostDataPoint {
  month: string;
  planned: number;
  emergency: number;
  parts: number;
}

/* ═══════════════ Driver Extended ═══════════════ */

export interface DriverProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  licenseNumber: string;
  licenseExpiry: string;
  licenseCategories: string[];
  hireDate: string;
  vehicleId?: string;
  vehiclePlate?: string;
  totalRequests: number;
  completedRequests: number;
  rating: number;
  status: 'На линии' | 'На базе' | 'На ремонте' | 'Выходной';
  shiftsThisMonth: number;
  totalMileage: number;
  avatar?: string;
}
