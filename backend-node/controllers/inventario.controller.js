const inventarioService = require("../services/inventario.service");

class InventarioController {

    listar(req, res) {
        res.json(inventarioService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            res.json(inventarioService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const item = inventarioService.crear(req.body);
            res.status(201).json({ mensaje: "Ítem registrado correctamente", item });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarCantidad(req, res) {
        try {
            const item = inventarioService.actualizarCantidad(req.params.id, req.body.cantidad);
            res.json(item);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const item = inventarioService.actualizarEstado(req.params.id, req.body.estado);
            res.json(item);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            inventarioService.eliminar(req.params.id);
            res.json({ mensaje: "Ítem eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new InventarioController();
