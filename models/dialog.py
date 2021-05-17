import pandas as pd

class Dialog:
    """
    Dialog structure.

    Parameters
    ----------
    dialog_id : int
        Unique dialog id.

    user_id : int
        User identifier.

    g_zscore : dict
        Global zscore for the movies.

    subgraph : DataFrame
        DataFrame of dialog graph.

    edgelist : DataFrame
        DataFrame of graph edges.

    """

    def __init__(
        self, 
        dialog_id: int, 
        user_id: int,
        g_zscore: dict,
        subgraph: pd.DataFrame, 
        edgelist: pd.DataFrame
    ):

        # Calling superclass constructor
        super().__init__()

        # Identifiers
        self.__dialog_id = dialog_id
        self.__user_id = user_id

        # Graph properties
        self.__edgelist = edgelist
        self.__subgraph = subgraph

        # Dialog properties
        self.__top = []
        self.__watched = []
        self.__dif_properties = []
        self.__prefered_prop = []
        self.__prefered_objects = []

        self.__p_chosen = ""
        self.__o_chosen = ""

        self.__g_zscore = g_zscore

    # region Getters and Setters
    def __set_watched(self, watched: str = None):
        self.__watched = watched

    def __get_watched(self):
        return self.__watched

    def __set_p_chosen(self, p_chosen: str = None):
        self.__p_chosen = p_chosen

    def __get_p_chosen(self):
        return self.__p_chosen
    
    def __set_o_chosen(self, o_chosen: str = None):
        self.__o_chosen = o_chosen

    def __get_o_chosen(self):
        return self.__o_chosen

    def __set_subgraph(self, subgraph: pd.DataFrame):
        self.__subgraph = subgraph

    def __get_subgraph(self):
        return self.__subgraph

    # endregion Getters and Setters

    # region Properties
      
    @property
    def watched(self):
        return self.__watched

    @property
    def edgelist(self):
        return self.__edgelist

    @property
    def prefered_objects(self):
        return self.__prefered_objects

    @property
    def prefered_prop(self):
        return self.__prefered_prop

    @property
    def top(self):
        return self.__top

    @property
    def dif_properties(self):
        return self.__dif_properties

    @property
    def full_prop_graph(self):
        return self.__full_prop_graph
        
    @property
    def user_id(self):
        return self.__user_id

    @property
    def g_zscore(self):
        return self.__g_zscore

    watched  = property(__get_watched, __set_watched)

    p_chosen = property(__get_p_chosen, __set_p_chosen)

    o_chosen = property(__get_o_chosen, __set_o_chosen)

    subgraph = property(__get_subgraph, __set_subgraph)

    # endregion Properties

    # region Class methods
    def prefered_infos(self, prefered_prop: list, prefered_objects: list):
        """
        Setting prefered properties and objects.
        Parameters
        ----------
        prefered_properties : list 
            Prefered properties.
        prefered_objects : list 
            Prefered objects.
        """
        self.__prefered_prop = prefered_prop
        self.__prefered_objects = prefered_objects

    def dialog_infos(
        self,
        watched: list,
        edgelist: pd.DataFrame,
        prefered_prop: list,
        prefered_objects: list
    ):
        """
        Setting watched list, edgelist and prefered properties and objects.
        Parameters
        ----------
        watched : list
            List of watched movies.
        edgelist : DataFrame
            DataFrame of graph edges.
        prefered_properties : list 
            Prefered properties.
        prefered_objects : list 
            Prefered objects.
        """
        self.__watched = watched
        self.__edgelist = edgelist
        self.prefered_infos(prefered_prop, prefered_objects)
    
    def dialog_properties_infos(self, top: pd.DataFrame, dif_properties: list):
        """
        Setting top of ordered movies and uniques properties.
        Parameters
        ----------
        top : DataFrame
            DataFrame of top of the ordered movies.
        dif_properties : list 
            List of uniques properties in the graph.
        """
        self.__top = top
        self.__dif_properties = dif_properties
    
    # endregion Class methods