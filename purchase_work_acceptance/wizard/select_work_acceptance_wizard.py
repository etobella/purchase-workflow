# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SelectWorkAcceptanceWizard(models.TransientModel):
    _name = 'select.work.acceptance.wizard'
    _description = 'Select Work Acceptance Wizard'

    require_wa = fields.Boolean(
        default=lambda self: self._get_require_wa(),
    )
    wa_id = fields.Many2one(
        comodel_name='work.acceptance',
        string='Work Acceptance',
        domain=lambda self: [
            ('state', '=', 'accept'),
            ('purchase_id', '=', self._context.get('active_id'))]
    )

    def _get_require_wa(self):
        return self.env.user.has_group(
            'purchase_work_acceptance.group_enforce_wa_on_invoice')

    @api.multi
    def button_create_vendor_bill(self):
        order = self.env['purchase.order'].browse(self._context.get('active_id'))
        if any(invoice.wa_id == self.wa_id for invoice in order.invoice_ids):
            raise ValidationError(_('%s was used in some bill.') % self.wa_id.name)
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        result['context'] = {
            'type': 'in_invoice',
            'default_wa_id': self.wa_id.id,
            'default_purchase_id': self._context.get('active_id'),
        }
        res = self.env.ref('account.invoice_supplier_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result
