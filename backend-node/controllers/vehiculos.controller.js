const vehiculosService = require("../services/vehiculos.service");

class VehiculosController {

    listar(req, res) {
        if (req.query.id_residencia) {
            return res.json(vehiculosService.obtenerPorResidencia(req.query.id_residencia));
        }
        res.json(vehiculosService.obtenerTodos());
    }

    obtener(req, res) {
        try {
            res.json(vehiculosService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const vehiculo = vehiculosService.crear(req.body);
            res.status(201).json({ mensaje: "Vehículo registrado correctamente", vehiculo });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const vehiculo = vehiculosService.actualizarEstado(req.params.id, req.body.estado);
            res.json(vehiculo);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            vehiculosService.eliminar(req.params.id);
            res.json({ mensaje: "Vehículo eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new VehiculosController();
