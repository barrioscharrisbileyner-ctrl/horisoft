const verificarToken = require("./authMiddleware");

function autorizarMetodos(rolesPorMetodo) {
    return (req, res, next) => {
        const metodo = req.method === "HEAD" ? "GET" : req.method;
        const roles = rolesPorMetodo[metodo];
        if (roles === null || (roles === undefined && ["GET", "OPTIONS"].includes(metodo))) {
            return next();
        }
        if (!Array.isArray(roles) || roles.length === 0) {
            return res.status(405).json({ mensaje: "Método no permitido" });
        }

        return verificarToken(req, res, () => {
            if (!roles.includes(req.usuario.rol)) {
                return res.status(403).json({ mensaje: "No tienes permiso para realizar esta acción" });
            }
            return next();
        });
    };
}

function exigirRoles(...rolesPermitidos) {
    return (req, res, next) => {
        if (!req.usuario || !rolesPermitidos.includes(req.usuario.rol)) {
            return res.status(403).json({ mensaje: "No tienes permiso para realizar esta acción" });
        }
        return next();
    };
}

module.exports = { autorizarMetodos, exigirRoles };
