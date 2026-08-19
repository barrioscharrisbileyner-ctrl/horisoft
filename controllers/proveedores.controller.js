const proveedoresService = require("../services/proveedores.service");

class ProveedoresController {

    listar(req, res) {
        res.json(proveedoresService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            res.json(proveedoresService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const proveedor = proveedoresService.crear(req.body);
            res.status(201).json({ mensaje: "Proveedor creado correctamente", proveedor });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const proveedor = proveedoresService.actualizarEstado(req.params.id, req.body.estado);
            res.json(proveedor);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            proveedoresService.eliminar(req.params.id);
            res.json({ mensaje: "Proveedor eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new ProveedoresController();
