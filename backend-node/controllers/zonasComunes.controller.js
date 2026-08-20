const zonasComunesService = require("../services/zonasComunes.service");

class ZonasComunesController {

    listar(req, res) {
        res.json(zonasComunesService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            const zona = zonasComunesService.obtenerPorId(req.params.id);
            res.json(zona);
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const zona = zonasComunesService.crear(req.body);

            res.status(201).json({
                mensaje: "Zona común creada correctamente",
                zona
            });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const zona = zonasComunesService.actualizarEstado(
                req.params.id,
                req.body.estado
            );
            res.json(zona);
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            zonasComunesService.eliminar(req.params.id);
            res.json({ mensaje: "Zona común eliminada" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new ZonasComunesController();
