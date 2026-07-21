/**
 * Unit Test — UC Xử lý đơn hàng
 * Assignee: Nguyễn Đức Cường
 *
 * Mocks included for ShipmentService and OrderService
 */

// --- Shipment Mocks ---
jest.mock("../../models/shipmentModel");
const ShipmentModel = require("../../models/shipmentModel");
const ShipmentService = require("../../services/shipmentService");

// --- Order Mocks ---
jest.mock("../../models", () => ({
  cartModel: {
    findById: jest.fn(),
    getCartItemsWithDetails: jest.fn(),
    clearCartItems: jest.fn(),
  },
  orderModel: {
    create: jest.fn(),
    addOrderItem: jest.fn(),
    findById: jest.fn(),
    findByIdWithDetails: jest.fn(),
    findByUserId: jest.fn(),
    countByUserId: jest.fn(),
    countOrderItems: jest.fn(),
    getOrderItems: jest.fn(),
    findAll: jest.fn(),
    count: jest.fn(),
    update: jest.fn(),
    updatePaymentStatus: jest.fn(),
  },
  productModel: {
    updateVariantStock: jest.fn(),
  },
  userModel: {},
}));

jest.mock("../../config/mysql", () => ({
  pool: {
    getConnection: jest.fn(),
  },
}));

const { cartModel, orderModel, productModel } = require("../../models");
const { pool } = require("../../config/mysql");
const OrderService = require("../../services/orderService");

const createMockConnection = () => ({
  beginTransaction: jest.fn().mockResolvedValue(),
  commit: jest.fn().mockResolvedValue(),
  rollback: jest.fn().mockResolvedValue(),
  release: jest.fn(),
});

describe("UC Xử lý đơn hàng - Shipment", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  describe("getShipment()", () => {
    test("UT_SHIP_001 - Trả về shipment object khi orderId tồn tại", async () => {
      const mockShipment = {
        order_id: 1,
        status: "shipping",
        tracking_code: "VN123",
      };
      ShipmentModel.findByOrderId.mockResolvedValue(mockShipment);
      const result = await ShipmentService.getShipment(1);
      expect(result).toEqual(mockShipment);
      expect(result).toHaveProperty("order_id", 1);
      expect(result).toHaveProperty("status", "shipping");
      expect(result).toHaveProperty("tracking_code", "VN123");
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledWith(1);
    });

    test("UT_SHIP_002 - Trả về null khi orderId không có shipment", async () => {
      ShipmentModel.findByOrderId.mockResolvedValue(null);
      const result = await ShipmentService.getShipment(9999);
      expect(result).toBeNull();
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledWith(9999);
    });

    test("UT_SHIP_006 - Throw lỗi khi model throw lỗi DB trong getShipment", async () => {
      ShipmentModel.findByOrderId.mockRejectedValue(new Error("Timeout"));
      await expect(ShipmentService.getShipment(1)).rejects.toThrow("Timeout");
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledWith(1);
    });

    test("UT_SHIP_015 - Trả về null khi orderId là string không phải số (service không validate kiểu)", async () => {
      ShipmentModel.findByOrderId.mockResolvedValue(null);
      const result = await ShipmentService.getShipment("abc");
      expect(result).toBeNull();
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledWith("abc");
    });

    test("UT_SHIP_017 - Phải throw lỗi khi orderId là chuỗi không phải số ('abc')", async () => {
      await expect(ShipmentService.getShipment("abc")).rejects.toThrow(
        "Invalid orderId",
      );
      expect(ShipmentModel.findByOrderId).not.toHaveBeenCalled();
    });
  });

  describe("updateShipment()", () => {
    test("UT_SHIP_003 - Gọi create() để tạo shipment mới khi chưa có shipment cho order này", async () => {
      const newShipment = {
        order_id: 1,
        status: "shipping",
        tracking_code: "VN123",
      };
      ShipmentModel.findByOrderId.mockResolvedValue(null);
      ShipmentModel.create.mockResolvedValue(newShipment);
      const shipmentData = { status: "shipping", tracking_code: "VN123" };
      const result = await ShipmentService.updateShipment(1, shipmentData);
      expect(result).toEqual(newShipment);
      expect(ShipmentModel.create).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.create).toHaveBeenCalledWith({
        order_id: 1,
        ...shipmentData,
      });
      expect(ShipmentModel.update).not.toHaveBeenCalled();
    });

    test("UT_SHIP_004 - Gọi update() để cập nhật shipment hiện có khi đã tồn tại cho order", async () => {
      const existingShipment = {
        order_id: 1,
        status: "shipping",
        tracking_code: "VN123",
      };
      const updatedShipment = {
        order_id: 1,
        status: "delivered",
        tracking_code: "VN123",
      };
      ShipmentModel.findByOrderId.mockResolvedValue(existingShipment);
      ShipmentModel.update.mockResolvedValue(updatedShipment);
      const shipmentData = { status: "delivered" };
      const result = await ShipmentService.updateShipment(1, shipmentData);
      expect(result).toEqual(updatedShipment);
      expect(result).toHaveProperty("status", "delivered");
      expect(ShipmentModel.update).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.update).toHaveBeenCalledWith(1, shipmentData);
      expect(ShipmentModel.create).not.toHaveBeenCalled();
    });

    test("UT_SHIP_005 - Throw lỗi khi model throw lỗi DB trong updateShipment", async () => {
      ShipmentModel.findByOrderId.mockRejectedValue(
        new Error("DB connection failed"),
      );
      await expect(
        ShipmentService.updateShipment(1, { status: "shipping" }),
      ).rejects.toThrow("DB connection failed");
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findByOrderId).toHaveBeenCalledWith(1);
    });

    test("UT_SHIP_014 - Tạo shipment mới khi shipmentData là object rỗng (service không validate data)", async () => {
      ShipmentModel.findByOrderId.mockResolvedValue(null);
      ShipmentModel.create.mockResolvedValue({ order_id: 1 });
      const result = await ShipmentService.updateShipment(1, {});
      expect(ShipmentModel.create).toHaveBeenCalledWith({ order_id: 1 });
      expect(result).toEqual({ order_id: 1 });
    });

    test("UT_SHIP_016 - Phải throw lỗi khi shipmentData là object rỗng {}", async () => {
      await expect(ShipmentService.updateShipment(1, {})).rejects.toThrow(
        "Shipment data cannot be empty",
      );
      expect(ShipmentModel.findByOrderId).not.toHaveBeenCalled();
    });
  });

  describe("getAllShipments()", () => {
    test("UT_SHIP_007 - Trả về danh sách tất cả shipments theo filters", async () => {
      const mockList = [
        { order_id: 1, status: "shipping", tracking_code: "VN001" },
        { order_id: 2, status: "delivered", tracking_code: "VN002" },
      ];
      ShipmentModel.findAll.mockResolvedValue(mockList);
      const filters = { status: "shipping" };
      const result = await ShipmentService.getAllShipments(filters);
      expect(result).toEqual(mockList);
      expect(result).toHaveLength(2);
      expect(ShipmentModel.findAll).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findAll).toHaveBeenCalledWith(filters);
    });

    test("UT_SHIP_008 - Trả về mảng rỗng khi không có shipment nào", async () => {
      ShipmentModel.findAll.mockResolvedValue([]);
      const result = await ShipmentService.getAllShipments({});
      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
      expect(ShipmentModel.findAll).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findAll).toHaveBeenCalledWith({});
    });

    test("UT_SHIP_009 - Dùng {} làm default filters khi không truyền argument", async () => {
      ShipmentModel.findAll.mockResolvedValue([]);
      await ShipmentService.getAllShipments();
      expect(ShipmentModel.findAll).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.findAll).toHaveBeenCalledWith({});
    });

    test("UT_SHIP_010 - Throw lỗi khi model throw lỗi DB trong getAllShipments", async () => {
      ShipmentModel.findAll.mockRejectedValue(new Error("Table not found"));
      await expect(ShipmentService.getAllShipments({})).rejects.toThrow(
        "Table not found",
      );
      expect(ShipmentModel.findAll).toHaveBeenCalledTimes(1);
    });
  });

  describe("deleteShipment()", () => {
    test("UT_SHIP_011 - Trả về kết quả xóa thành công khi orderId tồn tại", async () => {
      ShipmentModel.delete.mockResolvedValue({ affectedRows: 1 });
      const result = await ShipmentService.deleteShipment(1);
      expect(result).toEqual({ affectedRows: 1 });
      expect(ShipmentModel.delete).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.delete).toHaveBeenCalledWith(1);
    });

    test("UT_SHIP_012 - Trả về affectedRows=0 khi orderId không tồn tại", async () => {
      ShipmentModel.delete.mockResolvedValue({ affectedRows: 0 });
      const result = await ShipmentService.deleteShipment(9999);
      expect(result).toEqual({ affectedRows: 0 });
      expect(ShipmentModel.delete).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.delete).toHaveBeenCalledWith(9999);
    });

    test("UT_SHIP_013 - Throw lỗi khi model throw lỗi DB trong deleteShipment", async () => {
      ShipmentModel.delete.mockRejectedValue(
        new Error("Foreign key constraint"),
      );
      await expect(ShipmentService.deleteShipment(1)).rejects.toThrow(
        "Foreign key constraint",
      );
      expect(ShipmentModel.delete).toHaveBeenCalledTimes(1);
      expect(ShipmentModel.delete).toHaveBeenCalledWith(1);
    });
  });
});

describe("UC Xử lý đơn hàng - Order", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("updateOrder()", () => {
    test("UT_ORD_001 - Cập nhật đơn hàng thành công", async () => {
      orderModel.update.mockResolvedValue(true);
      const result = await OrderService.updateOrder(1, { status: "shipping" });
      expect(result).toBe(true);
      expect(orderModel.update).toHaveBeenCalledTimes(1);
      expect(orderModel.update).toHaveBeenCalledWith(1, { status: "shipping" });
    });

    test("UT_ORD_002 - Throw lỗi khi model throw lỗi DB trong updateOrder", async () => {
      orderModel.update.mockRejectedValue(new Error("DB error"));
      await expect(
        OrderService.updateOrder(1, { status: "shipping" }),
      ).rejects.toThrow("DB error");
      expect(orderModel.update).toHaveBeenCalledTimes(1);
    });
  });

  describe("updatePaymentStatus()", () => {
    test("UT_ORD_003 - Cập nhật payment status thành công", async () => {
      orderModel.updatePaymentStatus.mockResolvedValue(true);
      const result = await OrderService.updatePaymentStatus(1, "paid");
      expect(result).toBe(true);
      expect(orderModel.updatePaymentStatus).toHaveBeenCalledTimes(1);
      expect(orderModel.updatePaymentStatus).toHaveBeenCalledWith(1, "paid");
    });

    test("UT_ORD_004 - Throw lỗi khi model throw lỗi DB trong updatePaymentStatus", async () => {
      orderModel.updatePaymentStatus.mockRejectedValue(new Error("DB error"));
      await expect(OrderService.updatePaymentStatus(1, "paid")).rejects.toThrow(
        "DB error",
      );
      expect(orderModel.updatePaymentStatus).toHaveBeenCalledTimes(1);
    });
  });

  describe("getAllOrders()", () => {
    test("UT_ORD_005 - Trả về tất cả đơn hàng kèm pagination cho admin", async () => {
      const mockOrders = [
        {
          id: 1,
          user_name: "Nguyen Van A",
          user_email: "a@test.com",
          total_price: "250000",
          shipping_address: "123 Hà Nội",
          status: "pending",
          payment_status: "unpaid",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        },
      ];
      orderModel.findAll.mockResolvedValue(mockOrders);
      orderModel.count.mockResolvedValue(1);
      orderModel.countOrderItems.mockResolvedValue(2);

      const result = await OrderService.getAllOrders({ page: 1, limit: 20 });

      expect(result.orders).toHaveLength(1);
      expect(result.orders[0]).toEqual({
        id: 1,
        customer_name: "Nguyen Van A",
        customer_email: "a@test.com",
        total_price: 250000,
        shipping_address: "123 Hà Nội",
        status: "pending",
        payment_status: "unpaid",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
        total_items: 2,
      });
      expect(result.pagination).toEqual({
        page: 1,
        limit: 20,
        total: 1,
        total_pages: 1,
      });
      expect(orderModel.findAll).toHaveBeenCalledWith({ page: 1, limit: 20 });
      expect(orderModel.count).toHaveBeenCalledWith({ page: 1, limit: 20 });
    });

    test("UT_ORD_006 - Dùng default pagination khi không truyền filters", async () => {
      orderModel.findAll.mockResolvedValue([]);
      orderModel.count.mockResolvedValue(0);

      const result = await OrderService.getAllOrders({});

      expect(result.pagination).toEqual({
        page: 1,
        limit: 20,
        total: 0,
        total_pages: 0,
      });
    });

    test("UT_ORD_007 - Throw lỗi khi model throw lỗi DB trong getAllOrders", async () => {
      orderModel.findAll.mockRejectedValue(new Error("DB error"));
      await expect(OrderService.getAllOrders({})).rejects.toThrow("DB error");
      expect(orderModel.findAll).toHaveBeenCalledTimes(1);
    });

    test("UT_ORD_008 - Dùng default limit=20 khi gọi getAllOrders không truyền argument", async () => {
      orderModel.findAll.mockResolvedValue([]);
      orderModel.count.mockResolvedValue(0);

      const result = await OrderService.getAllOrders();

      expect(result.pagination.limit).toBe(20);
      expect(result.pagination.total_pages).toBe(0);
    });
  });

  describe("getOrderDetail()", () => {
    test("UT_ORD_009 - Trả về chi tiết đơn hàng khi orderId tồn tại", async () => {
      const mockOrder = {
        id: 1,
        user_id: 1,
        total_price: 250000,
        status: "pending",
        payment_status: "unpaid",
        shipping_address: "123 Hà Nội",
        items: [{ variant_id: 7, quantity: 2, price: 50000 }],
      };
      orderModel.findByIdWithDetails.mockResolvedValue(mockOrder);

      const result = await OrderService.getOrderDetail(1);

      expect(result).toEqual(mockOrder);
      expect(orderModel.findByIdWithDetails).toHaveBeenCalledTimes(1);
      expect(orderModel.findByIdWithDetails).toHaveBeenCalledWith(1);
    });

    test("UT_ORD_010 - Throw lỗi khi orderId không tồn tại", async () => {
      orderModel.findByIdWithDetails.mockResolvedValue(null);
      await expect(OrderService.getOrderDetail(9999)).rejects.toThrow(
        "Order not found",
      );
      expect(orderModel.findByIdWithDetails).toHaveBeenCalledTimes(1);
      expect(orderModel.findByIdWithDetails).toHaveBeenCalledWith(9999);
    });
  });
});
