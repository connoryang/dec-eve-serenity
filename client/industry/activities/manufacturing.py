#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\activities\manufacturing.py
import industry

class Manufacturing(industry.Activity):

    def job_modifiers(self, job):
        modifiers = []
        if job.materialEfficiency:
            modifiers.append(industry.MaterialModifier(1.0 - job.materialEfficiency / 100.0, reference=industry.Reference.BLUEPRINT))
        if job.timeEfficiency:
            modifiers.append(industry.TimeModifier(1.0 - job.timeEfficiency / 100.0, reference=industry.Reference.BLUEPRINT))
        return modifiers

    def job_max_runs(self, job):
        if job.blueprint.original:
            return industry.Activity.job_max_runs(self, job)
        else:
            return job.blueprint.runsRemaining

    def job_cost(self, job):
        return job.prices.get(job.blueprint.blueprintTypeID, 0) * float(job.runs)

    def job_output_products(self, job):
        output = []
        for product in self.products:
            output.append(industry.Material(typeID=product.typeID, quantity=job.runs * (product.quantity or 1)))

        return output

    def job_output_extras(self, job):
        blueprint = job.blueprint.copy()
        if not blueprint.original:
            blueprint.runsRemaining = max(blueprint.runsRemaining - job.runs, 0)
        return [blueprint]
