import pandas as pd

class Summary():
	def __init__(self, df):
		self.df = df

	def min_date(self):
		return self.df.Date.min().strftime('%Y-%m-%d')

	def count_visits(self):
		return len(self.df)

	def total_stores(self):
		return len(self.df.store_no.unique())

	def total_spend(self):
		total = self.df.Amount.sum()
		return ("%.2f" % total)

	def fav_store_no(self):
		return self.df[['store_no','Amount']].groupby(
			'store_no').agg({'Amount':'sum'}).sort_values(
			'Amount', ascending=False)[:1].index[0]

	def fav_store_city(self):
		add = self.df['short_address'][
			self.df.store_no == self.fav_store_no()].unique()[0][1:].split(',')[0]
		city =  self.df['city'][self.df.store_no == self.fav_store_no()].unique()[0]
		return '%s in %s'%(add, city)

	def spend_avg(self):
		avg =  float(self.total_spend())/self.count_visits()
		return ("%.2f" % avg)



	def format_args(self):
		return dict(
			min_date = self.min_date(),
			count_visits = self.count_visits(),
			total_stores = self.total_stores(),
			total_spend = self.total_spend(),
			fav_store_no = self.fav_store_no(),
			fav_store_city = self.fav_store_city(),
			spend_avg = self.spend_avg()
			)



	def markdown(self):
		md = """
Since **{min_date}** Chipotle has been visited **{count_visits}** times.

Across **{total_stores}** different locations **${total_spend}** worth of Chipotle has been ordered.

The favorite store is Store **{fav_store_no}** at **{fav_store_city}**

On average **${spend_avg}** is spent on a visit to Chipotle.

Scroll down to learn more about Chipotle behavior of the Chipotme users.
""".format(**self.format_args())
		return md


